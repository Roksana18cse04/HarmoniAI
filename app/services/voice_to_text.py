import requests
import time
import os
from dotenv import load_dotenv
from app.services._get_prediction import get_prediction

# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
def create_prediction(audio_url):
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "incredibly-fast-whisper",
            "version": "0.0.1",
            "input": {
  "task": "transcribe",
  "audio": audio_url,
  "hf_token": HF_TOKEN,
  "language": "None",
  "timestamp": "chunk",
  "batch_size": 24,
  "diarise_audio": False
},
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

