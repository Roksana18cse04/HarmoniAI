import requests
import time
import os
from app.services.image_get_prediction import get_prediction
from app.services.textToImage_create_prediction import create_prediction
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def imageGenerate(image_request) -> dict:
    try:
        # Create prediction and get prediction ID
        prediction_id = create_prediction(image_request.prompt, image_request.model_name)
        
        # Get the image URL
        image_url = get_prediction(prediction_id)

        # If an image URL was returned, return the prompt and the image URL
        if image_url:
            return {"prompt": image_request.prompt, "image_url": image_url}
        else:
            return {"prompt": image_request.prompt, "image_url": None}
    except Exception as e:
        # Handle any errors during the process
        print(f"Error generating image: {e}")
        return {"prompt": image_request.prompt, "image_url": None}