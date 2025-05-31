import requests
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from app.services.image_get_prediction import get_prediction

# Load environment variables
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def background_remove_create_prediction(image_url:str):
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "rembg",
            "version": "0.0.1",
            "input": {
  "image": image_url
},
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]
    
    
def image_backgroun_remove(image_url:str):
    try:
        prediction_id = background_remove_create_prediction(image_url)
       # Create prediction
        print(f"Prediction created: {prediction_id}")    
        # Get result
        result = get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result['output']
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    image_url = "https://storage.googleapis.com/1019uploads/7b7a24ba-6c15-4081-8106-0d9430e7cde9.png"
    image_backgroun_remove(image_url)
    