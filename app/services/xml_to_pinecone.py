import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from app.services.parse_xml import get_products_from_xml

# === Load API Keys ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")

# === Init OpenAI & Pinecone Clients ===
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("shopping-products")

# === Config ===
BATCH_SIZE = 100  # Tune based on latency and input size limits

# === Batch Embedding Function ===
def embed_products_in_batches(products):
    print("Start batch embedding...")

    vectors = []
    total_batches = (len(products) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num in range(total_batches):
        start = batch_num * BATCH_SIZE
        end = start + BATCH_SIZE
        batch = products[start:end]

        texts = [f"{p['title']} {p['color']} {p['gender']} {p['price']}" for p in batch]

        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
        except Exception as e:
            print(f"Embedding failed for batch {batch_num + 1}: {e}")
            continue

        for j, embedding in enumerate(embeddings):
            vectors.append((
                f"prod_{start + j}",  # Unique and ordered ID
                embedding,
                batch[j]
            ))

        print(f"Embedded batch {batch_num + 1} of {total_batches}")

    print(f"Total vectors created: {len(vectors)}")
    return vectors

# === Upsert to Pinecone ===
def upsert_products(products):
    print("Upsert function start---------------")
    vectors = embed_products_in_batches(products)

    if vectors:
        index.upsert(vectors)
        print(f"Upserted {len(vectors)} products to Pinecone.")
    else:
        print("No vectors to upsert.")

# === Single Text Embedding for Querying ===
def embed_text(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Failed to embed query text: {e}")
        return None

# === Query Pinecone ===
def query_products(user_prompt, top_k=10):
    print("Query function start-----------")
    query_vector = embed_text(user_prompt)

    if not query_vector:
        return []

    try:
        response = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        print("Query completed and response-----", response)
        return [match['metadata'] for match in response.matches]
    except Exception as e:
        print(f"Query failed: {e}")
        return []

# === Fetch and Index All Products ===
def fetch_and_index_all_products():
    urls = [
        "https://www.kappa-tr.com/feed/standartV3",
        "https://tr.ecco.com/feed/googleV2",
        "https://www.suvari.com.tr/feed/googleV2",
        "https://www.alvinaonline.com/tr/p/XMLProduct/GoogleMerchantXML",
        "https://www.perspective.com.tr/feed/facebook",
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
    upsert_products(all_products)
