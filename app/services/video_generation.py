import requests
from app.schemas.TextToVedio import TextToVideoRequest
from app.services._get_prediction import get_prediction
import time
import os
from dotenv import load_dotenv
load_dotenv(override=True)
 
API_KEY =  os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
 
def create_prediction(prompt: str, model_name: str, duration: int):
    url= "https://api.eachlabs.ai/v1/prediction/"
    playload = {
            "model": model_name,
            "version": "0.0.1",
            "input": {
                "prompt": prompt,
                "cfg_scale" : 0.5,
                "prompt_optimizer": False,
                "negative_prompt": "blur, distort, and low quality",
                "aspect_ratio": "16:9",
                "seed": 9999,
                "quality": "540p",
                "duration": duration,
                "motion_mode": "normal",
                "model_name": model_name,
            }
    }
 
    response = requests.post(url, headers=HEADERS, json= playload)
           
    prediction = response.json()
    print(f"Prediction response: {prediction}")  # Debugging line
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    return prediction,playload
