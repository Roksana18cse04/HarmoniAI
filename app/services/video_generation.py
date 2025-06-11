import requests
from app.schemas.TextToVedio import TextToVideoRequest
from app.services._get_prediction import get_prediction
import time
import os
from dotenv import load_dotenv
load_dotenv(override=True)
 
API_KEY =  os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
 
def create_prediction(prompt: str, model_name: str, duration: int):
    url= "https://api.eachlabs.ai/v1/prediction/"
    payload = {
            "model": model_name,
            "version": "0.0.1",
            "input": {
                "prompt": prompt,
                "cfg_scale" : 0.5,
                "prompt_optimizer": False,
                "negative_prompt": "blur, distort, and low quality",
                "aspect_ratio": "16:9",
                "seed": 9999,
                "quality": "540p",
                "duration": duration,
                "motion_mode": "normal",
                "model_name": model_name,
            }
    }
 
    response = requests.post(url, headers=HEADERS, json= payload)
           
    prediction = response.json()
    print(f"Prediction response: {prediction}")  # Debugging line
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    return prediction["predictionID"]
 
def generate_video(data: TextToVideoRequest) -> str:
    # Generate a video based on the prompt, model name, and duration
    prediction_id = create_prediction(data.model_name, data.prompt, data.duration)
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

    try:
        # Generate video and get the result
        from app.schemas.TextToVedio import TextToVideoRequest
        
        data = TextToVideoRequest(
            prompt=prompt,
            model_name=model_name,
            duration=duration
        )
        video_url = generate_video(data)
        if video_url:
            print(f"Generated video URL: {video_url}")
        else:
            raise Exception("No video URL returned.")
    except Exception as e:
        print(f"Error: {e}")

