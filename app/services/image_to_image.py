import requests
import time
import os
from app.config import ImageRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def create_prediction(model_name,image_url, style_slug,prompt):
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": model_name,
            "version": "0.0.1",
            "input": {
                "image_url_1": image_url,
                "style_slug": style_slug,
                "prompt": prompt
            }
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]
