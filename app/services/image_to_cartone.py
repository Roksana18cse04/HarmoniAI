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

def image_to_cartone_create_prediction(input_image: str, ) -> str:
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "cartoonify",
            "version": "0.0.1",
            "input": {
  "seed": 9999,
  "image": input_image,  # Change from input_image/image_url
},
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

def image_to_cartone_generate(input_image:str):
    try:
        prediction_id = image_to_cartone_create_prediction(input_image)
        result = get_prediction(prediction_id)
        if result:
            print(f"Output URL: {result['output']}")
            print(f"Processing time: {result['metrics']['predict_time']}s")
        return result
    except Exception as e:
        print(f"Error during image to cartoon conversion: {e}")
        return None
    
# Example usage:
if __name__ == "__main__":
    input_image = "https://t4.ftcdn.net/jpg/02/14/74/61/360_F_214746128_31JkeaP6rU0NzzzdFC4khGkmqc8noe6h.jpg"
    result = image_to_cartone_generate(input_image)
    if result:
        print(f"Cartoonified image URL: {result['output']}")
    else:
        print("Failed to cartoonify the image.")