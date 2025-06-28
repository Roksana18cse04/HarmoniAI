import requests
import time
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv(override=True)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
    
def create_prediction(audio_url:str,image_url:str):
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "omnihuman",
            "version": "0.0.1",
            "input": {
            "mode": "normal",
            "audio_url": audio_url,
            "image_url": image_url
        },
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction

