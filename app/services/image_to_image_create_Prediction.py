import requests
import os
import time

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def create_prediction(model_name: str, prompt: str, image_url: str, style_slug: str) -> str:
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": model_name,
            "version": "0.0.1",
            "input": {
                "input_image": image_url,
                "prompt": prompt,
                "style": style_slug,  
                "output_format": "webp",
                "output_quality": 90
            },
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

def get_prediction(prediction_id):
    while True:
        result = requests.get(
            f"https://api.eachlabs.ai/v1/prediction/{prediction_id}",
            headers=HEADERS
        ).json()
        print(f"Prediction status: {result}")
        if result["status"] == "success":
            return result
        elif result["status"] == "error":
            raise Exception(f"Prediction failed: {result}")
        
        time.sleep(1)  # Wait before polling again