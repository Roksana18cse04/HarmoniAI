from openai import OpenAI
from app.services.parse_xml import get_products_from_xml
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv(override=True)

API_KEY =  os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)  # Or use OpenRouter

def shopping_agent(user_prompt):
    urls = [
        "https://www.kappa-tr.com/feed/standartV3",
        "https://tr.ecco.com/feed/googleV2",  # Add more URLs here
        "https://www.suvari.com.tr/feed/googleV2",
        "https://www.alvinaonline.com/tr/p/XMLProduct/GoogleMerchantXML",
        "https://www.perspective.com.tr/feed/facebook",

    ]

    all_products = []
    for url in urls:
        try:
            products = get_products_from_xml(url)
            all_products.extend(products)
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
    
    print(f"Total products fetched: {len(all_products)}") 

    # product_list = get_products_from_xml("https://www.kappa-tr.com/feed/standartV3")
    product_text = "\n".join([ 
        f"- {p['title']} | {p['color']} | {p['gender']} | {p['price']} | {p['link']} | {p['image']}"
        for p in all_products[:30]
    ])


    prompt = f"""You are a helpful shopping assistant.
Here is a list of products:
{product_text}

Now answer this user query: "{user_prompt}"

Return the best matches with title, price, link and image.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    print(f"Shopping agent response: {response.choices[0].message.content}")  # Debugging line
    return response.choices[0].message.content


