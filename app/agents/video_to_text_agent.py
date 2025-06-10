import os
from app.services.video_to_text import get_prediction,create_prediction


def video_to_text_generate(video_url:str):
    # Create a new prediction
    try:
    # Create prediction
        prediction_id = create_prediction(video_url)
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        result = get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result['output']
    except Exception as e:
        print(f"Error: {e}")
        
#example 

# videourl = "https://youtube.com/clip/UgkxN99U_gg843KkMt8f8-gGT_h5wPuXqkGo?si=7CiORF51d8nkNHrK"
# video_to_text_generate(videourl)
