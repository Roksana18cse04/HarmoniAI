from app.services.VideoGenerationWithAudio import create_prediction
from app.services._get_prediction import get_prediction

def generate_video_with_audio(audio_url: str, image_url: str): 
    # Generate video using the audio 
    try:
        response, model_info= create_prediction(audio_url,image_url)
        prediction_id = response['predictionID']
        result = get_prediction(prediction_id)
        if result.get("status") == "success":
            return result, model_info
        else:
            raise Exception("Video generation failed: No output URL found.")
    except Exception as e:
        print(f"Error while fetching prediction: {e}")
        raise e
    