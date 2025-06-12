import requests
import os
import time

from openai import OpenAI
from dotenv import load_dotenv
from app.services._get_prediction import get_prediction

# Load environment variables
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
def image_style_enhanche_create_prediction(prompt: str, source_image: str, style_image: str):
    # Get image from user
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "multi-image-kontext",
            "version": "0.0.1",
            "input": {
                "seed": 9999,
                "prompt": prompt,
                "aspect_ratio": "match_input_image",
                "input_image_1": source_image,
                "input_image_2": style_image
            },
            "webhook_url": ""
        }
    )
    prediction = response.json()

    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")

    return prediction["predictionID"]

def image_style_and_color_change(prompt: str, source_image: str, style_image: str):
    try:
        # Define your prompt, source_image, and style_image variables here
        prediction_id = image_style_enhanche_create_prediction(prompt, source_image, style_image)
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        result = get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result['output']
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    # Test the function

    source_image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRc7u6bc5fdfAXTebU78knx9Y5n7b9z05MhDA&s"
    style_image = "https://images.pexels.com/photos/906150/pexels-photo-906150.jpeg?auto=compress&cs=tinysrgb&w=600"
    prompt =(f"A photo of the reimagined {source_image} in the style of {style_image}")



    result = image_style_and_color_change(prompt, source_image, style_image)
    print(f"car new ------>",result)
    
    