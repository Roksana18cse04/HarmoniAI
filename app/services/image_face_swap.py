import requests
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
    
def face_swap_create_prediction(swap_image_url: str,input_image_url:str):# balri image
    playload ={
            "model": "face-swap-new",
            "version": "0.0.1",
            "input": {
                "swap_image": swap_image_url,
                "input_image": input_image_url
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
def face_swap(swap_image_url, input_image_url) :
    # Define the input and swap imagestry:
    try:
        # Create prediction
        response,model_info = face_swap_create_prediction(swap_image_url, input_image_url)
        prediction_id = response['predictionID']
        
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        result = face_swap_get_prediction(prediction_id)
        return result,model_info
    except Exception as e:
        print(f"Error: {e}")
    