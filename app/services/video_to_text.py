import requests
import time
import os

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
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "youtube-transcriptor",
            "version": "0.0.1",
            "input": {
  "url": video_url
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
        
        if result["status"] == "success":
            return result
        elif result["status"] == "error":
            raise Exception(f"Prediction failed: {result}")
        
        time.sleep(1)  # Wait before polling again
        
