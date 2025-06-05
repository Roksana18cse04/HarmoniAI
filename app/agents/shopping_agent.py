import os
from dotenv import load_dotenv
from openai import OpenAI
# from app.services.xml_to_faiss import query_products  # Your existing XML parser
from app.services.product_weaviate import query_weaviate_products
import json

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# === SHOPPING AGENT ===
def shopping_agent(user_prompt):
    relevant_products = query_weaviate_products(user_prompt, top_k=10)

    print("relevant products -----------", relevant_products)

    product_text = "\n".join([
        f"- Title: {p['title']}, Color: {p['color']}, Gender: {p['gender']}, Price: {p['price']}, Link: {p['link']}, Image_link: {p['image_link']}"
        for p in relevant_products
    ])

    prompt = f"""You are a helpful shopping assistant.  
Here is a list of relevant products:  
{product_text}  

The user asks: "{user_prompt}"  

**Task:**  
1. Select **up to 5** best-matching products (fewer if not enough are relevant).  
2. Return them as a **valid JSON array** with each item containing:  
   - `title` (string)  
   - `price` (string/number)  
   - `link` (string, URL)  
   - `image` (string, URL/path)  

**Rules:**  
- Only include products that truly match the query.  
- If no products match, return an empty array `[]`.  
- Respond **ONLY with JSON**, no additional text.  

Example output format:  
```json
[
    {{
        "title": "Product Name",
        "price": "$19.99",
        "link": "https://example.com/product",
        "image": "https://example.com/image.jpg"
    }}
]
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw response:")
        print(response.choices[0].message.content)
        return {"error": "Invalid JSON returned from model"}


