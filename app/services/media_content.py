from app.config import config
import os
import json
import logging
from app.services.weaviate_client import client
from app.services.helper import safe_float
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI
import asyncio
from weaviate.classes.data import DataObject
from weaviate.classes.query import MetadataQuery

# # === Load ENV & API Key ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Init Clients ===
openai_client = OpenAI(api_key=OPENAI_API_KEY)
weaviate_client = client

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
            if category_title in ['Kitab', 'Müzik'] else
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
        "image": content.get("image", ""),
        "creator": (
            next((a.get("name", "") for a in content.get("author", []) if isinstance(a, dict)), "")
            if category_title == 'Kitab' else
            next((d.get("name", "") for d in content.get("directors", []) if isinstance(d, dict)), "")
            if category_title in ['Film', 'Dizi'] else
            ", ".join(content.get("details", {}).get("artists", []))
            if category_title == 'Müzik' and isinstance(content.get("details", {}).get("artists"), list) else
            str(content.get("details", {}).get("artists", ""))
            if category_title == 'Müzik' else
            ""
        ),

        "releaseYear": (
            int(content.get("publish_year"))
            if category_title == 'Kitab' and content.get("publish_year") and str(content.get("publish_year")).isdigit() else
            int(str(content.get("publish_time", ""))[:4])
            if category_title in ['Film', 'Dizi'] and content.get("publish_time") and str(content.get("publish_time", ""))[:4].isdigit() else
            int(content.get("release_year"))
            if category_title == 'Müzik' and content.get("release_year") and str(content.get("release_year")).isdigit() else
            None
        ),

        "tags": (
            [g.get("title") for g in content.get("details", {}).get("genres", [])]
            if category_title in ['Kitab', 'Müzik'] else
            [g.get("title") for g in content.get("details", {}).get("genres", {}).get("value", [])]
            if category_title in ['Film', 'Dizi'] else
            []
        ),

        "rating": (
            safe_float(content.get("rating", {}).get("value")) or
            safe_float(content.get("book_rating")) or
            0.0
        ),

        "duration": (
            str(content.get("details", {}).get("duration_time", {}).get("value", ""))
            if category_title in ['Film', 'Dizi'] and content.get("details", {}).get("duration_time", {}).get("value") else
            str(content.get("duration", ""))
            if category_title == 'Müzik' and content.get("duration") else
            ""
        ),

        "link": link,

        "actors": (
            [actor.get("name") for actor in content.get("actors", []) if isinstance(actor, dict)]
            if category_title in ['Film', 'Dizi'] else
            []
        ),

        "publisher": (
            content.get("details", {}).get("publisher", "")
            if category_title == 'Kitab' else
            ""
        )
    }

    # Remove fields with None, empty string, or empty list values
    return {k: v for k, v in processed.items() if v not in [None, "", []]}

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
    data=data[:500]
    try:
        # Get the collection
        if not weaviate_client.is_connected():
            weaviate_client.connect()
        content_collection = weaviate_client.collections.get("ContentItem")
        
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
            item_vector_pairs = generate_content_embeddings(processed_items)
            if not item_vector_pairs:
                logger.error("Failed to generate embeddings for the batch, skipping this chunk")
                continue

            # Prepare data objects for batch insert
            data_objects = []
            for processed_item, vector in item_vector_pairs:
                data_objects.append(
                    DataObject(
                        properties=processed_item,
                        vector=vector
                    )
                )

            # Insert all objects at once using batch_insert
            try:
                response = content_collection.data.insert_many(data_objects)
                
                # Check for any errors
                if response.has_errors:
                    for error in response.errors:
                        logger.error(f"Failed to import: {error}")
                else:
                    logger.info(f"Successfully imported {len(data_objects)} items in batch {i//BATCH_SIZE + 1}")
                    
            except Exception as e:
                logger.error(f"Batch import failed for chunk {i//BATCH_SIZE + 1}: {e}")
                
                # Fallback to individual inserts
                logger.info("Attempting individual inserts for this chunk...")
                successful_imports = 0
                for processed_item, vector in item_vector_pairs:
                    try:
                        uuid = content_collection.data.insert(
                            properties=processed_item,
                            vector=vector
                        )
                        logger.info(f"Imported: {processed_item.get('title', 'Unknown')} with UUID: {uuid}")
                        successful_imports += 1
                    except Exception as individual_error:
                        logger.error(f"Failed to import {processed_item.get('title', 'Unknown')}: {individual_error}")
                
                logger.info(f"Successfully imported {successful_imports} out of {len(item_vector_pairs)} items individually")

    except Exception as e:
        logger.error(f"Import process failed: {e}")

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
        # Updated query for Weaviate v4
        if not weaviate_client.is_connected():
            weaviate_client.connect()
        content_collection = weaviate_client.collections.get("ContentItem")
        
        response = content_collection.query.near_vector(
            near_vector=query_vector,
            limit=top_k,
            return_metadata=MetadataQuery(distance=True)
        )
        
        return [obj.properties for obj in response.objects]

    except Exception as e:
        print("Query error:", e)
        return []
    
def fetch_all_media(): 
    try:
        base_dir = Path(config.BASE_DIR).parent
        content_path = os.path.join(base_dir, "Remzi", "omuz.n_contents.json")
        categories_path = os.path.join(base_dir, "Remzi", "omuz.n_categories.json")
        
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
    except Exception as e:
        logger.error(f"Failed to fetch and import media: {e}")
    finally:
        weaviate_client.close()
    
    
# # === Entrypoint ===

# if __name__ == "__main__":
#     from app.config import config
#     base_dir = Path(config.BASE_DIR).parent
#     content_path = os.path.join(base_dir, "Remzi", "omuz.n_contents.json")
#     categories_path = os.path.join(base_dir, "Remzi", "omuz.n_categories.json")

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
#                 res = process_content_for_weaviate(content_item, category_map)
#                 print(res)

#             # for d in data:
#             #     if d.get("category_ids") == '5fec4ff395675ff6952edeb1':
#             #         print(d)
#             #         break

#             # import_content_to_weaviate(data, category_map)
#         finally:
#             weaviate_client.close()  # ✅ Proper cleanup to avoid warning

#     asyncio.run(main())