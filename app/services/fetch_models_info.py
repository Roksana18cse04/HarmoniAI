import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)

EACHLABS_API_KEY = os.getenv("EACHLABS_API_KEY")

def fetch_models_info():
    url = "https://crm.eachlabs.ai/v1/models"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": EACHLABS_API_KEY  # Include this if the API requires it
    }
    payload = {
        "jsonrpc": 2.0,
        "params": {
            "limit": 50,
            "offset": 0
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        models = response.json()
        return models
    else:
        raise Exception(f"Error: {response.status_code} {response.text}")




