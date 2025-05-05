import requests
import os
from dotenv import load_dotenv
load_dotenv()

EACHLAB_API_KEY = os.getenv("EACHLAB_API_KEY")

def fetch_models_by_category_id(category_id: int):
    url = "https://eachlab.ai/ai-tools-by-category"
    headers = {
        "Authorization": f"Bearer {EACHLAB_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "category_id": category_id
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tools = data["result"]["result"]  # This is typically a list of tools/models
        return [tool["name"] for tool in tools]
    else:
        raise Exception(f"Error fetching tools: {response.status_code} {response.text}")