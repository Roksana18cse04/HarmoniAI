import os
from dotenv import load_dotenv
from openai import OpenAI
from app.services.xml_to_faiss import query_products  # Your existing XML parser

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# === SHOPPING AGENT ===
def shopping_agent(user_prompt):
    relevant_products = query_products(user_prompt, top_k=10)
    print("relevant product-----------", relevant_products)

    product_text = "\n".join([
        f"- {p['title']} | {p['color']} | {p['gender']} | {p['price']} | {p['link']} | {p['image']}"
        for p in relevant_products
    ])

    prompt = f"""You are a helpful shopping assistant.
Here is a list of relevant products:
{product_text}

Now answer this user query: "{user_prompt}"

Return the best matches with title, price, link and image.
"""
    response = client.chat.completions.create(  
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content

