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
            response = requests.get(
                f"https://api.eachlabs.ai/v1/prediction/{prediction_id}",
                headers=HEADERS
            )
            response.raise_for_status()
            result = response.json()

            print("Response:", result)  # Debugging

            if isinstance(result, dict) and result.get("status") == "success":
                if "output" in result:
                    # Handle both cases: output as list or direct URL
                    if isinstance(result["output"], list) and len(result["output"]) > 0:
                        image_url = result["output"][0]  # Get first URL from list
                    elif isinstance(result["output"], str):
                        image_url = result["output"]  # Direct URL string
                    else:
                        print("Error: 'output' format not recognized.")
                        return None

                    print(f"Image generation successful: {image_url}")
                    return image_url
                else:
                    print("Error: 'output' key missing in response.")
                    return None
            elif result.get("status") in ["error", "cancelled"]:
                print(f"Error: {result.get('message', 'Generation failed')}")
                return None

            print("Processing...")
            time.sleep(3)
    except requests.exceptions.RequestException as e:
        print(f"Error polling prediction: {e}")
        return None
    
    
