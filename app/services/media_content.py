from app.config import config
import os
import json
import logging
from app.services.weaviate_client import client
from app.services.helper import safe_float
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI
import asyncio
# # === Load ENV & API Key ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Init Clients ===
openai_client = OpenAI(api_key=OPENAI_API_KEY)
weaviate_client= client
# === Config ===
BATCH_SIZE = 100

# === Process Content to Weaviate Format ===
def process_content_for_weaviate(content: Dict, category_map: Dict) -> Dict:
    category_id = content.get("category_ids")
    category_title = category_map.get(category_id, f"Unknown ({category_id})")

    #Handle link: pick the first one from remote_links
    remote_links = content.get("remote_links", "")
    if isinstance(remote_links, str):
        link = remote_links
    elif isinstance(remote_links, dict):
        link = next(iter(remote_links.values()), "")
    else:
        link = ""

    processed = {
        "title": content.get("title", ""),
        "category": category_title,

        "genre_list": (
            [g.get("title", "").lower() for g in content.get("details", {}).get("genres", [])]
            if category_title in ['Kitap', 'Müzik'] else
            [g.get("title", "").lower() for g in content.get("details", {}).get("genres", {}).get("value", [])]
            if category_title in ['Film', 'Dizi'] else
            []
        ),

        "language": (
            content.get("details", {}).get("language")
            or content.get("localization", "").split("-")[0]
            if content.get("localization")
            else ""
        ),

        "description": content.get("description", ""),
        "image": content.get("image"),
        "creator": (
            next((a.get("name", "") for a in content.get("author", []) if isinstance(a, dict)), "")
            if category_title == 'Kitap' else
            next((d.get("name", "") for d in content.get("directors", []) if isinstance(d, dict)), "")
            if category_title in ['Film', 'Dizi'] else
            content.get("details", {}).get("artists", [])
            if category_title == 'Müzik' else
            ""
        ),

        "releaseYear": (
            int(content.get("publish_year"))
            if category_title == 'Kitap' and content.get("publish_year") else
            int(str(content.get("publish_time", ""))[:4])
            if category_title in ['Film', 'Dizi'] and content.get("publish_time") else
            int(content.get("release_year"))
            if category_title == 'Müzik' and content.get("release_year") else
            None
        ),

        "tags": (
            [g.get("title") for g in content.get("details", {}).get("genres", [])]
            if category_title in ['Kitap', 'Müzik'] else
            [g.get("title") for g in content.get("details", {}).get("genres", {}).get("value", [])]
            if category_title in ['Film', 'Dizi'] else
            []
        ),

        "rating": (
            safe_float(content.get("rating", {}).get("value")) or
            safe_float(content.get("book_rating"))
        ),

        "duration": (
            content.get("details", {}).get("duration_time", {}).get("value", "")
            if category_title in ['Film', 'Dizi'] else
            content.get("duration", "")
            if category_title == 'Müzik' else
            None
        ),

        "link": link,

        "actors": (
            [actor.get("name") for actor in content.get("actors", []) if isinstance(actor, dict)]
            if category_title in ['Film', 'Dizi'] else
            []
        ),

        "publisher": (
            content.get("details", {}).get("publisher", "")
            if category_title == 'Kitap' else
            ""
        )
    }

    # Remove fields with None, empty string, or empty list values
    # return {k: v for k, v in processed.items() if v not in [None, "", []]}
    return processed

def generate_content_embeddings(items: list[dict]) -> list[tuple[dict, list[float]]]:
    """
    Generate OpenAI embeddings for a list of content metadata dictionaries.
    Returns list of (item, embedding) tuples.
    """
    texts = []
    cleaned_items = []

    for item in items:
        text_input = " ".join([
            item.get("title", ""),
            item.get("category", ""),
            ", ".join(item.get("genre_list", [])),
            item.get("language", ""),
            item.get("description", ""),        
            item.get("creator", ""),
            ", ".join(item.get("tags", [])),
            ", ".join(item.get("actors", [])),
            item.get("publisher", "")
        ])
        text_input = text_input.lower().strip()
        texts.append(text_input)
        cleaned_items.append(item)  # Keep same order

    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        vectors = [r.embedding for r in response.data]
        return list(zip(cleaned_items, vectors))  # ⬅ return tuples of (item, vector)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []



# === Load Data and Import to Weaviate ===
def import_content_to_weaviate(data, category_map):
    for i in range(0, len(data), BATCH_SIZE):
        chunk = data[i:i + BATCH_SIZE]

        # Preprocess all items in the chunk
        processed_items = []
        for item in chunk:
            processed_item = process_content_for_weaviate(item, category_map)
            if not processed_item.get("title"):
                continue
            processed_items.append(processed_item)

        # Generate embeddings for all processed items in the chunk
        vectors = generate_content_embeddings(processed_items)
        if not vectors:
            logger.error("Failed to generate embeddings for the batch, skipping this chunk")
            continue

        # Add each item with its embedding vector to the batch
        for processed_item, vector in zip(processed_items, vectors):
            try:
                weaviate_client.batch.add_data_object(
                    data_object=processed_item,
                    class_name="ContentItem",
                    vector=vector
                )
                logger.info(f"Imported: {processed_item['title']}")
            except Exception as e:
                logger.error(f"Failed to import: {e}")

    # Flush any remaining objects in the batch
    try:
        weaviate_client.batch.flush()
    except Exception as e:
        logger.warning(f"Flush failed: {e}")

    logger.info("Import completed.")



# === Embed text ===
def embed_text(text: str):
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None
    
def query_weaviate_media(user_prompt: str, top_k: int = 10):
    """Query Weaviate for content items based on user prompt."""
    query_vector = embed_text(user_prompt)
    if query_vector is None:
        print("Embedding failed for prompt:", user_prompt)
        return []

    try:
        result = weaviate_client.query.get(
            "ContentItem",
            [
                "title", "category", "genre_list", "language", "description",
                "image", "creator", "releaseYear", "tags", "rating",
                "duration", "link", "actors", "publisher"  # fixed 'actors'
            ]
        ).with_near_vector({
            "vector": query_vector  # removed .tolist()
        }).with_limit(top_k).do()

        return result.get("data", {}).get("Get", {}).get("ContentItem", [])

    except Exception as e:
        print("Query error:", e)
        return []
    
def fetch_all_media(): 
    try:
        base_dir = Path(config.BASE_DIR).parent
        content_path=os.path.join(base_dir, "Remzi", "omuz.n_contents.json")
        categories_path=os.path.join(base_dir, "Remzi", "omuz.n_categories.json")
        # Load category map
        with open(categories_path, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        category_map = {
            cat.get("_id", {}).get("$oid"): cat.get("title", "")
            for cat in categories_data if cat.get("_id") and cat.get("title")
        }

        # Load content
        with open(content_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Loaded {len(data)} content items.")
        import_content_to_weaviate(data, category_map)
    finally:
            weaviate_client.close()
    
    
# # === Entrypoint ===

# if __name__ == "__main__":
#     from app.config import config
#     base_dir = Path(config.BASE_DIR).parent
#     content_path=os.path.join(base_dir, "Remzi", "omuz.n_contents.json")
#     categories_path=os.path.join(base_dir, "Remzi", "omuz.n_categories.json")

#     async def main():
#         try:
#             with open(categories_path, 'r', encoding='utf-8') as f:
#                 categories_data = json.load(f)
#             category_map = {
#                 cat.get("_id", {}).get("$oid"): cat.get("title", "")
#                 for cat in categories_data if cat.get("_id") and cat.get("title")
#             }

#             with open(content_path, 'r', encoding='utf-8') as f:
#                 data = json.load(f)

#             # Process first 50 items
#             for content_item in data[:50]:
#                 res= process_content_for_weaviate(content_item, category_map)
#                 print(res)

#             # for d in data:
#             #     if d.get("category_ids") == '5fec4ff395675ff6952edeb1':
#             #         print(d)
#             #         break

#             # import_content_to_weaviate(content_path, categories_path)
#         finally:
#             weaviate_client.close()  # ✅ Proper cleanup to avoid warning

#     asyncio.run(main())


