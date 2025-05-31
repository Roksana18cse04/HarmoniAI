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

def create_prediction_baby_image(man_image_url:str,gender:str,Women_image_url):
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "each-baby",
            "version": "0.0.1",
            "input": {
  "seed": 9999,
  "image": man_image_url,
  "steps": 25,
  "width": 512,
  "gender": gender,
  "height": 728,
  "image2": Women_image_url,
},
        "webhook_url": ""
    }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

def baby_face(man_image_url,gender,Women_image_url):
    try:
        prediction_id = create_prediction_baby_image(man_image_url,gender,Women_image_url)
        print(f"Prediction created: {prediction_id}")
        # Get result
        result = get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result['output']
    except Exception as e:
        print(f"Error: {e}")
        return e


if __name__ == "__main__":
    man_image_url = "https://t4.ftcdn.net/jpg/02/14/74/61/240_F_214746128_31JkeaP6rU0NzzzdFC4khGkmqc8noe6h.jpg"
    Woman_image_url ="https://t4.ftcdn.net/jpg/03/37/76/73/240_F_337767352_vgswVhGx5tmc58JFa3CLZDDnb9vTn4sY.jpg"
    gender = "girl"
    baby_face(man_image_url,gender,Woman_image_url)