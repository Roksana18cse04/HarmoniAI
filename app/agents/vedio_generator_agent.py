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