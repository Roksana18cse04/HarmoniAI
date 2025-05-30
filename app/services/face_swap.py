import requests
import os
import time

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
    
def face_swap_create_prediction(swap_image_url: str,input_image_url:str):# balri image
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "face-swap-new",
            "version": "0.0.1",
            "input": {
  "swap_image": swap_image_url,
  "input_image": input_image_url
},
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

def face_swap_get_prediction(prediction_id: str):  
    while True:
        result = requests.get(
            f"https://api.eachlabs.ai/v1/prediction/{prediction_id}",
            headers=HEADERS
        ).json()
        
        if result["status"] == "success":
            return result
        elif result["status"] == "error":
            raise Exception(f"Prediction failed: {result}")
        
        time.sleep(3)  # Wait before polling again
        

def face_swap_new(swap_image_url: str,input_image_url:str):
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "each-faceswap-v1",
            "version": "0.0.1",
            "input": {
  "target_image_gif_or_video": swap_image_url,
  "source_image": input_image_url
},
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]
def image_swap(swap_image_url, input_image_url):
    """
    Swaps faces between two images using the EachLabs API.
    
    :param swap_image_url: URL of the image to swap faces with.
    :param input_image_url: URL of the input image to apply the face swap on.
    :return: Prediction ID of the face swap operation.
    """
    try:
        # Create prediction
        prediction_id = face_swap_new(swap_image_url, input_image_url)
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        result = face_swap_get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
    except Exception as e:
        print(f"Error: {e}")
    
    return face_swap_create_prediction(swap_image_url, input_image_url)
#example uses
if __name__ == "__main__":
    input_image_url = "https://plus.unsplash.com/premium_photo-1661329937685-e9e4eb06a36a?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    swap_image_url= "https://images.unsplash.com/photo-1613876215075-276fd62c89a4?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    try:
        # Create prediction
        prediction_id = face_swap_create_prediction(swap_image_url, input_image_url)
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        result = face_swap_get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        print("Face swap completed successfully.")
        output = image_swap(swap_image_url, input_image_url)
        print(f"Output: {output['output']}")
    except Exception as e:
        print(f"Error: {e}")