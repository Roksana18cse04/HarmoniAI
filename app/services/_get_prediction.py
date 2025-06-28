import requests
import time
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def get_prediction(prediction_id: str) -> str:
    try:
        while True:
    
            result = requests.get(
                f"https://api.eachlabs.ai/v1/prediction/{prediction_id}",
                headers=HEADERS
            ).json()
            if result["status"] == "success":
                print(f"Prediction result:---------get--------- {result}")
                return result
            elif result["status"] == "error":
                raise Exception(f"Prediction failed: {result}")
            print("Processing...")
            time.sleep(3)
    except requests.exceptions.RequestException as e:
        print(f"Error polling prediction: {e}")
        return e
    
    
