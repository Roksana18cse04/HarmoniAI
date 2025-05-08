from openai import OpenAI
from app.services.parse_xml import get_products_from_xml
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv(override=True)

API_KEY =  os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)  # Or use OpenRouter

def query_gpt(user_prompt, product_list):
    product_text = "\n".join([ 
        f"- {p['title']} | {p['color']} | {p['gender']} | {p['price']} | {p['link']}"
        for p in product_list[:30]
    ])

    prompt = f"""You are a helpful shopping assistant.
Here is a list of products:
{product_text}

Now answer this user query: "{user_prompt}"

Return the best matches (max 5) with title, price, and link.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    
    return response.choices[0].message.content


if __name__ == "__main__":
    # Run it
    products = get_products_from_xml("https://www.kappa-tr.com/feed/standartV3")
    user_input = "I want a white unisex hat"
    result = query_gpt(user_input, products)
    print(result)

