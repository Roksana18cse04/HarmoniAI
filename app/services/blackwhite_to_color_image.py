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
def drw_image_color_create_prediction(image_url: str, prompt: str):
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "sdxl-controlnet",
            "version": "0.0.1",
            "input": {
                "seed": 9999,
                "image":image_url,
                "prompt": prompt,
                "condition_scale": 0.5,
                "negative_prompt": "low quality, bad quality, sketches",
                "num_inference_steps": 50
            },
            "webhook_url": ""
        }
    )
    prediction = response.json()
    
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

def draw_image_color(image_url: str, prompt: str):
    try:
        prediction_id = drw_image_color_create_prediction(image_url, prompt)
       # Get result
        result = get_prediction(prediction_id)
        # print(f"Output URL: {result['output']}")
        # print(f"Processing time: {result['metrics']['predict_time']}s")
        return result['output']
    except Exception as e:
        print(f"Error: {e}")

# example usage
if __name__ == "__main__":
    image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSzlt7C5lzPRFT4kFge_euWovwOlkjfljrM1g&s"
    prompt = "image colorizations  of  a wite horse and green field"
    try:
        colored_image = draw_image_color(image_url, prompt)
        print("Colored image URL:", colored_image)
    except Exception as e:
        print("Error:", str(e))
    