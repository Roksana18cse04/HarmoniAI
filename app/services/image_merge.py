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
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "eachlabs-couple",
            "version": "0.0.1",
            "input": {
                "prompt": prompt,
                "reference_image": image_url_1,
                "input_image": image_url_2
            },
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

def image_merge(prompt,image_url_1,image_url_2):
    try:
        prediction_id = create_merge_image_prediction(prompt, image_url_1, image_url_2)
        print(prediction_id)
        result=get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result['output']
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    prompt = "a couple in cristmas market and looking at the camera"
    image_url_1 = "https://storage.googleapis.com/magicpoint/models/women.png"
    image_url_2 = "https://storage.googleapis.com/magicpoint/models/man.png"
    image_merge(prompt, image_url_1, image_url_2)