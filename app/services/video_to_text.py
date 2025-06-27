import requests
import time
import os
from app.services._get_prediction import get_prediction

from openai import OpenAI
from dotenv import load_dotenv


# Load environment variables
load_dotenv(override=True)

# Initialize OpenAI client with the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def create_prediction(video_url:str):
    playload = {
            "model": "youtube-transcriptor",
            "version": "0.0.1",
            "input": {
                "url": video_url
            },
            "webhook_url": ""
        }
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json=playload
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return {
        "prediction_id": prediction["predictionID"],
        "model_info": playload
    }

