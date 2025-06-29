import requests
import time
from app.services._get_prediction import get_prediction
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv(override=True)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
 
def prduct_photo_create_prediction(prompt, input_image_1, input_image_2):
    playload = {
        "model": "product-shoot",
        "version": "0.0.1",
        "input": {
            "input_image_2": input_image_1,
            "input_image_1": input_image_2,
            "aspect_ratio": "match_input_image",
            "prompt": prompt
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

def product_photo_generate(prompt, input_image_1, input_image_2):
    try:
        response, model_info = prduct_photo_create_prediction(prompt, input_image_1, input_image_2)
        prediction_id = response["predictionID"]
        result = get_prediction(prediction_id)
        if result["status"] == "success":
            return result, model_info
        else:
            print(f"Prediction failed with status: {result['status']}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None 

