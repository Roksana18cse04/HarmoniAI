import requests
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
  "duration": duration,
  "mode": "PRO",
  "model_name": model_name,
  "prompt": prompt,
}
    }
 
    response = requests.post(url, headers=HEADERS, json= payload)
           
    prediction = response.json()
    print(f"Prediction response: {prediction}")  # Debugging line
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
 
 
def generate_video(prompt: str, model_name: str, duration: int) -> str:
    # Generate a video based on the prompt, model name, and duration
    prediction_id = create_prediction(prompt, model_name, duration)
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
        video_url = generate_video(prompt, model_name, duration)
        if video_url:
            print(f"Generated video URL: {video_url}")
        else:
            raise Exception("No video URL returned.")
    except Exception as e:
        print(f"Error: {e}")
