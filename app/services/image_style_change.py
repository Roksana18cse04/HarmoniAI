from PIL import Image
import requests
from io import BytesIO
import requests
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from app.services._get_prediction import get_prediction

# Load environment variables
load_dotenv(override=True)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
# 3d,realistic_style,angel,anime_style,japanese_comics,princess_style,dreamy,ink_style,new_monet_garden,monets_garden,exquisite_comic,cyber_machinery,chinese_style,romantic,ugly_clay,cute_doll,3d_gaming,animated_movie,doll",
def create_style_prediction(style_slug, image_url):
    print(image_url)
    print(style_slug)
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "bytedance",
            "version": "0.0.1",
            "input": {
                "style": style_slug,
                "image_url": image_url
            },
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

def style_change(style_slug: str, image_url: str):
    
    try:
        # Create prediction
        prediction_id = create_style_prediction(style_slug, image_url)
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        result = get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result['output']
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    image_url = "https://cdn.pixabay.com/photo/2025/05/19/13/34/girl-9609522_640.jpg"
    style_slug = "chinese_style"
    style_change(style_slug, image_url)
    