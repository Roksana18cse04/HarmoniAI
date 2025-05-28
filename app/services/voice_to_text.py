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
def create_prediction():
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "incredibly-fast-whisper",
            "version": "0.0.1",
            "input": {
  "task": "transcribe",
  "audio": "your_file.audio/mp3",
  "hf_token": "your hf token here",
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