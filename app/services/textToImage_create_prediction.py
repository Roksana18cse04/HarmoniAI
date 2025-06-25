import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def create_prediction(prompt: str,model_name : str) -> str:
    payload = {
            "model": model_name,
            "version": "0.0.1",
            "input": {
                "prompt": prompt,
                "aspect_ratio": "1:1",
                "output_format": "webp",
                "output_quality": 90,    
            },   
            "webhook_url": ""
        }
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json=payload
    )
    print(response)
    response.raise_for_status()
    prediction = response.json()
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    return {
        "pred_id": prediction["predictionID"],
        "model_info": payload
    }