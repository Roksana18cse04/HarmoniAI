import requests
import time
import os
from dotenv import load_dotenv
from app.services._get_prediction import get_prediction

# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def create_merge_image_prediction(prompt:str,image_url_1:str,image_url_2:str):
    playload = {
        "model": "eachlabs-couple",
        "version": "0.0.1",
        "input": {
            "prompt": prompt,
            "reference_image": image_url_1,
            "input_image": image_url_2
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
    
    return prediction,playload

def image_merge(prompt,image_url_1,image_url_2):
    try:
        response,model_info = create_merge_image_prediction(prompt, image_url_1, image_url_2)
        # Create prediction
        prediction_id = response['predictionID']
        print(prediction_id)
        result=get_prediction(prediction_id)
        return result,model_info
    except Exception as e:
        print(f"Error: {e}")

