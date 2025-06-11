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
import ijson
import numpy as np

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
BATCH_SIZE = 1000

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
                if response.has_errors:
                    for error in response.errors:
                        logger.error(f"Batch {i // BATCH_SIZE + 1} error: {error}")
                else:
                    logger.info(f"✅ Successfully imported {len(data_objects)} items in batch {i // BATCH_SIZE + 1}")
            except Exception as e:
                logger.warning(f"⚠️ Batch insert failed for batch {i // BATCH_SIZE + 1}: {e}")
                logger.info("Attempting individual fallback insert...")
                success = 0
                for item, vec in item_vector_pairs:
                    try:
                        uuid = content_collection.data.insert(properties=item, vector=vec)
                        logger.debug(f"Inserted {item.get('title', 'Unknown')} with UUID {uuid}")
                        success += 1
                    except Exception as ind_e:
                        logger.error(f"Failed individual insert: {item.get('title', 'Unknown')} - {ind_e}")
                logger.info(f"✅ Individually imported {success}/{len(item_vector_pairs)} items in batch {i // BATCH_SIZE + 1}")

    except Exception as e:
        logger.error(f"Import process failed: {e}")

    logger.info("Import completed.")

# === Embed text ===
def embed_text(text):
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    except Exception as e:
        print(f"Failed to embed query text: {e}")
        return None
    
def query_weaviate_media(user_prompt, top_k: int = 10):
    """Query Weaviate for content items based on user prompt."""
    query_vector = embed_text(user_prompt)
    print("type------------", type(query_vector))
    if query_vector is None:
        print("Embedding failed for prompt:", user_prompt)
        return []

    try:
        # Updated query for Weaviate v4
        if not weaviate_client.is_connected():
            weaviate_client.connect()
        media_collection = weaviate_client.collections.get("ContentItem")
        
        response = media_collection.query.hybrid(
            query=user_prompt,
            vector=query_vector.tolist(),  # manually provided embedding
            alpha=0.5,
            limit=top_k,
            return_metadata=MetadataQuery(score=True)
        )
        
        return [obj.properties for obj in response.objects]

    except Exception as e:
        print("Query error:", e)
        return []
    
import requests    

def fetch_all_media(batch_size=1000): 
    try:
        content_url = "https://cdn.harmoniai.net/omuz.n_contents.json"
        categories_url = "https://cdn.harmoniai.net/omuz.n_categories.json"

        # Load categories once (small JSON)
        cat_res = requests.get(categories_url)
        if cat_res.status_code != 200:
            logger.error(f"Failed to load categories: {cat_res.status_code}")
            return

        categories_data = cat_res.json()
        category_map = {
            cat.get("_id", {}).get("$oid"): cat.get("title", "")
            for cat in categories_data if cat.get("_id") and cat.get("title")
        }

        # Stream content items
        content_res = requests.get(content_url, stream=True)
        if content_res.status_code != 200:
            logger.error(f"Failed to load content: {content_res.status_code}")
            return

        logger.info("Streaming content items...")

        items = ijson.items(content_res.raw, 'item')
        batch = []
        count = 0

        for item in items:
            batch.append(item)
            if len(batch) >= batch_size:
                import_content_to_weaviate(batch, category_map)
                count += len(batch)
                batch = []
                logger.info(f"Imported {count} content items.")

        # Import any remaining items
        if batch:
            import_content_to_weaviate(batch, category_map)
            count += len(batch)

        logger.info(f"Imported {count} content items.")

    except Exception as e:
        logger.error(f"Failed to fetch and import media: {e}")
    finally:
        weaviate_client.close()

        
        