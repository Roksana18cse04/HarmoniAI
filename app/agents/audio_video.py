
from app.schemas.video_with_audio import VideoWithAudioRequest
from app.services.VideoGenerationWithAudio import create_prediction, get_prediction




def generate_video_with_audio(data:VideoWithAudioRequest): 
    # Generate video using the audio URL
    prediction_id = create_prediction(data.audio_url,data.image_url)
    
    try:
        video_url = get_prediction(prediction_id)
        url = video_url.get("output")
        if url:
            return url
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
