 
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv(override=True)
 
API_KEY =  os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
 
def create_prediction():
    url= "https://api.eachlabs.ai/v1/prediction/"
    payload = {
            "model": "kling-ai-image-to-video",
            "version": "0.0.1",
            "input": {
  "duration": 10,
  "image_url": "https://storage.googleapis.com/magicpoint/models/man.png",
  "mode": "PRO",
  "model_name": "kling-v1-6",
  "prompt": "a man who is shouting very loudly",
}
    }
 
    response = requests.post(url, headers=HEADERS, json= payload)
           
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
 
try:
    # Create prediction
    prediction_id = create_prediction()
    print(f"Prediction created: {prediction_id}")
   
    # Get result
    result = get_prediction(prediction_id)
    print(f"Output URL: {result['output']}")
    print(f"Processing time: {result['metrics']['predict_time']}s")
except Exception as e:
    print(f"Error: {e}")
 
   
