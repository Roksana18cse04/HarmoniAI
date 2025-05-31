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

    source_image = "https://images.unsplash.com/photo-1704340142770-b52988e5b6eb?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDF8MHxzZWFyY2h8MXx8Y2FyfGVufDB8fDB8fHww"
    style_image = "https://as1.ftcdn.net/v2/jpg/04/15/39/62/1000_F_415396222_fKXCicBqfPPkOdxyWkT5l8GBkenJNfkt.jpg"

    prompt = (
    f"Apply the pattern, texture, and colors from the style image ({style_image}) and source image color yello glossyfiber as a high-quality custom wrap on the car in the source image ({source_image}). "
    f"The entire vehicle surface — including the hood, roof, doors, and sides — should be wrapped fully in the style. "
    f"Preserve all reflections, lighting, and surface contours of the car for realism. "
    f"The wrap should appear vivid, glossy, and metallic. Do not change the background — only apply the style to the car body."
)



    result = image_style_and_color_change(prompt, source_image, style_image)
    print(f"car new ------>",result)
    