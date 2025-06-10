import numpy as np
from app.services.parse_xmlProduct import get_products_from_xml
from app.services.weaviate_client import client
from openai import OpenAI
from dotenv import load_dotenv
import os
import weaviate.classes as wvc
from weaviate.classes.query import MetadataQuery


# === Load API Keys ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Init OpenAI Client ===
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# === Config ===
BATCH_SIZE = 100

# === Batch Embedding Function ===
def embed_products_in_batches(products):
    print("Start batch embedding...")

    vectors = []
    metadata = []

    total_batches = (len(products) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num in range(total_batches):
        start = batch_num * BATCH_SIZE
        end = start + BATCH_SIZE
        batch = products[start:end]

        texts = [f"{p['title']} {p['color']} {p['gender']} {p['price']} {p['link']} {p['image_link']}" for p in batch]

        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            embeddings = [np.array(e.embedding, dtype=np.float32) for e in response.data]
        except Exception as e:
            print(f"Embedding failed for batch {batch_num + 1}: {e}")
            continue

        vectors.extend(embeddings)
        metadata.extend(batch)
        print(f"Embedded batch {batch_num + 1} of {total_batches}")

    print(f"Total vectors created: {len(vectors)}")
    return vectors, metadata

from more_itertools import chunked
def upsert_products_to_weaviate(products):
    import time
      # Optional if you want clean chunking

    max_batch_size = 50  # Reduce to avoid gRPC timeout errors
    products = products[:500]  # Limit total for test run
    print("Upserting to Weaviate...")

    vectors, metadata = embed_products_in_batches(products)

    # Ensure client is connected
    if not client.is_connected():
        client.connect()

    product_collection = client.collections.get("Product")

    # Prepare all data objects
    data_objects = []
    for product, vector in zip(metadata, vectors):
        data_object = wvc.data.DataObject(
            properties={
                "title": product["title"],
                "color": product["color"],
                "gender": product["gender"],
                "price": product["price"],
                "link": product["link"],
                "image_link": product["image_link"],
            },
            vector=vector.tolist() if hasattr(vector, "tolist") else vector
        )
        data_objects.append(data_object)

    # Chunk and insert in batches to avoid timeout
    for i, chunk in enumerate(chunked(data_objects, max_batch_size)):
        try:
            response = product_collection.data.insert_many(chunk)
            if response.has_errors:
                print(f"Batch {i+1} had {len(response.errors)} errors:")
                for error in response.errors:
                    print(f"Error: {error}")
            else:
                print(f"Batch {i+1}: Successfully upserted {len(chunk)} products.")
        except Exception as e:
            print(f"Batch {i+1} insert failed: {e}")
            time.sleep(2)  # Delay before retrying next batch

# === Single Text Embedding ===
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

# === Query Weaviate ===
def query_weaviate_products(user_prompt, top_k=10):
    query_vector = embed_text(user_prompt)
    if query_vector is None:
        print("Embedding failed for prompt:", user_prompt)
        return []

    try:
        # Get the Product collection
        if not client.is_connected():
            client.connect()
        product_collection = client.collections.get("Product")
        
        # Perform vector search
        response = product_collection.query.near_vector(
            near_vector=query_vector.tolist(),
            limit=top_k,
            return_metadata=MetadataQuery(distance=True)
        )
        
        # Extract products from response
        products = []
        for item in response.objects:
            product = {
                "title": item.properties.get("title"),
                "color": item.properties.get("color"),
                "gender": item.properties.get("gender"),
                "price": item.properties.get("price"),
                "link": item.properties.get("link"),
                "image_link": item.properties.get("image_link"),
                "distance": item.metadata.distance if item.metadata else None
            }
            products.append(product)
        
        if not products:
            print("No results found for:", user_prompt)

        # Check total count of products
        print("Fetching total products...")
        aggregate_response = product_collection.aggregate.over_all(
            total_count=True
        )
        print(f"Total products in collection: {aggregate_response.total_count}")

        return products

    except Exception as e:
        print("Query error:", e)
        return []

import json
def deduplicate_products(products):
    seen = set()
    unique = []
    for p in products:
        key = json.dumps(p, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique

# === Fetch and Index All Products ===
def fetch_and_index_all_products():  
    urls = [
        "https://www.kappa-tr.com/feed/standartV3",
        # "https://tr.ecco.com/feed/googleV2",
        # "https://www.suvari.com.tr/feed/googleV2",
        # "https://www.alvinaonline.com/tr/p/XMLProduct/GoogleMerchantXML",
        # "https://www.perspective.com.tr/feed/facebook",
    ]

    all_products = []
    for url in urls:
        try:
            products = get_products_from_xml(url)
            all_products.extend(products)
            print(f"Fetched {len(products)} from {url}")
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")

    print(f"Total fetched products: {len(all_products)}")
    products = deduplicate_products(all_products)
    upsert_products_to_weaviate(products)