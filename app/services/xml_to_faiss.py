import os
import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from app.services.parse_xml import get_products_from_xml
import pickle

# === Load API Keys ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Init OpenAI Client ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === Config ===
BATCH_SIZE = 100
FAISS_INDEX_PATH = "faiss_index.index"
METADATA_PATH = "metadata.pkl"

# === Global FAISS Index and Metadata ===
faiss_index = None
product_metadata = []

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

        texts = [f"{p['title']} {p['color']} {p['gender']} {p['price']}" for p in batch]

        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            embeddings = [np.array(item.embedding, dtype=np.float32) for item in response.data]
        except Exception as e:
            print(f"Embedding failed for batch {batch_num + 1}: {e}")
            continue

        vectors.extend(embeddings)
        metadata.extend(batch)
        print(f"Embedded batch {batch_num + 1} of {total_batches}")

    print(f"Total vectors created: {len(vectors)}")
    return vectors, metadata

# === FAISS Upsert ===
def upsert_products(products):
    global faiss_index, product_metadata

    print("Upsert function start---------------")
    vectors, metadata = embed_products_in_batches(products)

    if not vectors:
        print("No vectors to upsert.")
        return

    dim = len(vectors[0])
    if faiss_index is None:
        faiss_index = faiss.IndexFlatL2(dim)

    vectors_np = np.vstack(vectors)
    faiss_index.add(vectors_np)
    product_metadata.extend(metadata)

    # Save index and metadata
    faiss.write_index(faiss_index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump(product_metadata, f)

    print(f"Upserted {len(vectors)} products to FAISS.")

# === Single Text Embedding ===
def embed_text(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    except Exception as e:
        print(f"Failed to embed query text: {e}")
        return None

# === Query FAISS ===
def query_products(user_prompt, top_k=10):
    global faiss_index, product_metadata

    print("Query function start-----------")
    if faiss_index is None or not product_metadata:
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
            faiss_index = faiss.read_index(FAISS_INDEX_PATH)
            with open(METADATA_PATH, 'rb') as f:
                product_metadata = pickle.load(f)
        else:
            print("FAISS index or metadata not found.")
            return []

    query_vector = embed_text(user_prompt)
    if query_vector is None:
        return []

    query_vector = np.expand_dims(query_vector, axis=0)
    distances, indices = faiss_index.search(query_vector, top_k)
    print(f"Query returned {len(indices[0])} results.")
    
    return [product_metadata[i] for i in indices[0] if i < len(product_metadata)]

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
