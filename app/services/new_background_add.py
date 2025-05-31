from PIL import Image
import requests
from io import BytesIO
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

def add_background_from_url(object_url: str, background_url: str, output_path: str):
    # Load transparent object image from URL
    obj_response = requests.get(object_url)
    obj = Image.open(BytesIO(obj_response.content)).convert("RGBA")

    # Load background image from URL
    bg_response = requests.get(background_url)
    bg = Image.open(BytesIO(bg_response.content)).convert("RGBA")
    bg = bg.resize(obj.size)

    # Composite the object onto the background
    final = Image.alpha_composite(bg, obj)

    # Save the final image
    final.save(output_path)
    print(f"✅ Saved final image with background: {output_path}")

def create_prediction_foradd(object_url:str,background_url:str,prompt):
    response = requests.post(
    "https://api.eachlabs.ai/v1/prediction/",
    headers=HEADERS,
    json={
        "model": "flux-fill-pro",
        "version": "0.0.1",
        "input": {
  "mask": background_url,
  "seed": 9999,
  "image": object_url,
  "steps": 50,
  "prompt":prompt,
  "guidance": 3,
  "output_format": "jpg",
  "safety_tolerance": 2,
  "prompt_upsampling": False
},
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

def add_background(image_url:str,background_url:str,prompt):
    try:
        # Create prediction
        prediction_id = create_prediction_foradd(image_url,background_url,prompt)
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        result = get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result['output']
    except Exception as e:
        print(f"Error: {e}")
# === Example usage ===
if __name__ == "__main__":
    object_url = "https://storage.googleapis.com/1019uploads/ce57bd9d-6f2a-4892-9e7b-9dd3d2f1cd72.png"            # Car image with transparent BG
    background_url = "https://img.freepik.com/premium-photo/searchlight-neon-brick-wall-with-smoke-neon-reflections-wet-asphalt-empty-scene-with-copy-space_117255-1836.jpg?semt=ais_hybrid&w=740"   # New background image
    output_path = "car_with_new_bg.png"
    prompt = (f"please add a car to the background image")

    add_background_from_url(object_url, background_url, output_path)
    add_background(object_url,background_url,prompt)
