import requests
import os
from app.schemas.TextToImage import TextToImageRequest
from dotenv import load_dotenv
from app.services.textToImage_create_prediction import create_prediction
from app.services._get_prediction import get_prediction
# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def text_to_generate_image(image_request: TextToImageRequest) -> dict:
    prompt = image_request.prompt
    model_name = image_request.eachlabs_model_name
    intend = getattr(image_request.intend, "intend", None)
    try:
        # Create prediction and get prediction ID
        response = create_prediction(prompt,model_name)
        prediction_id = response['pred_id']
        
        # Get the image URL
        result = get_prediction(prediction_id)
        image_url=result['output']
        intend = image_request.intend

        if image_url:
            return result, response['model_info']
    except Exception as e:
        # Handle any errors during the process
        print(f"Error generating image: {e}")

        return {
            "prompt": image_request.prompt, 
            "intend": intend, 
            "image_url": None
        }
