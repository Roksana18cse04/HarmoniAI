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


def create_prediction(prompt: str,model_name : str) -> str:
    """
    Create a prediction request to the Each Labs API.

    Args:
        prompt (str): The text prompt for image generation.

    Returns:
        str: The prediction ID.
    """
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": model_name,
            "version": "0.0.1",
            # "input": {
            #     "prompt": prompt,
            #     "guidance": 3.5,
            #     "num_outputs": 1,
            #     "aspect_ratio": "1:1",
            #     "output_format": "webp",
            #     "output_quality": 90,
            #     "prompt_strength": 0.8,
            #     "num_inference_steps": 28
            # }
            "input": {
                "prompt": prompt,
                "aspect_ratio": "1:1",
                "output_format": "webp",
                "output_quality": 90,    
            }   
        }
    )
    response.raise_for_status()
    prediction = response.json()
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    return prediction["predictionID"]