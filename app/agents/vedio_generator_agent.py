 
import requests
import time
import os
from app.services.video_generation import get_prediction,create_prediction 
from app.schemas.TextToVedio import TextToVideoRequest
from dotenv import load_dotenv
load_dotenv(override=True)
 
API_KEY =  os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
 
def create_prediction():
    url= "https://api.eachlabs.ai/v1/prediction/"
    payload = {
            "model": "kling-ai-image-to-video",
            "version": "0.0.1",
            "input": {
  "duration": 10,
  "image_url": "https://storage.googleapis.com/magicpoint/models/man.png",
  "mode": "PRO",
  "model_name": "kling-v1-6",
  "prompt": "a man who is shouting very loudly",
}
    }
 
    response = requests.post(url, headers=HEADERS, json= payload)
           
    prediction = response.json()
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    return prediction["predictionID"]
 
def get_prediction(prediction_id):
    while True:
        result = requests.get(
            f"https://api.eachlabs.ai/v1/prediction/{prediction_id}",
            headers=HEADERS
        ).json()
       
        if result["status"] == "success":
            return result
        elif result["status"] == "error":
            raise Exception(f"Prediction failed: {result}")
       
        time.sleep(1)  # Wait before polling again
 
try:
    # Create prediction
    prediction_id = create_prediction()
    print(f"Prediction created: {prediction_id}")
   
    # Get result
    result = get_prediction(prediction_id)
    print(f"Output URL: {result['output']}")
    print(f"Processing time: {result['metrics']['predict_time']}s")
except Exception as e:
    print(f"Error: {e}")

def text_to_video_generate(data:TextToVideoRequest):
    prediction_id = create_prediction( data.prompt, data.model_name, data.duration)
    try:
        video_url = get_prediction(prediction_id)
        url = video_url.get("output")
        if url:
            return url
        else:
            raise Exception("Video generation failed: No output URL found.")
    except Exception as e:
        print(f"Error while fetching prediction: {e}")
        raise

# Example usage
if __name__ == "__main__":
    prompt = input("Enter the prompt for video generation: ")
    model_name = input("Enter the model name: ")
    duration = int(input("Enter the duration (in seconds): "))
    data = TextToVideoRequest(prompt=prompt,model_name=model_name,  duration=duration)

    try:
        # Generate video and get the result
        video_url = text_to_video_generate(data)
        if video_url:
            print(f"Generated video URL: {video_url}")
        else:
            raise Exception("No video URL returned.")
    except Exception as e:
        print(f"Error: {e}")
