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
import requests
import time
def create_prediction_for_dress_trail(cloth_image_url: str, human_image_url: str) -> str:
    """    Create a prediction for the dress trial image using the EachLabs API.
    Args:
        cloth_image_url (str): URL of the cloth image.
        human_image_url (str): URL of the human image.
        Returns:
        str: The prediction result.
    """
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "eachlabs-custom-vto",
            "version": "0.0.1",
            "input": {
  "cloth_image": cloth_image_url,
  "human_image": human_image_url,
},
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]
