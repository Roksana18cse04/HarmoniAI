
from app.services.VideoGenerationWithAudio import create_prediction
from app.services._get_prediction import get_prediction




def generate_video_with_audio(audio_url: str, image_url: str): 
    # Generate video using the audio 
    try:
        response = create_prediction(audio_url,image_url)
        prediction_id = response['predictionID']
        print(f"Prediction ID: ---agents--- {prediction_id}")
        print(f"Model Info: {response['model_info']}")
        result = get_prediction(prediction_id)
        if result.get("status") == "success":
            return response,result
        else:
            raise Exception("Video generation failed: No output URL found.")
    except Exception as e:
        print(f"Error while fetching prediction: {e}")
        raise e
    
if __name__ == "__main__":
    # Example usage
    audio_url = input("Enter the audio URL: ")  
    image_url = input("Enter the image URL: ")
    data = VideoWithAudioRequest(audio_url=audio_url, image_url=image_url)
    print(generate_video_with_audio(data))
