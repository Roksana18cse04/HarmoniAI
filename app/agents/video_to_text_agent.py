import os
from app.services.video_to_text import get_prediction,create_prediction
def video_to_text_generate(video_url:str):
    # Create a new prediction
    try:
    # Create prediction
        response ,model_info= create_prediction(video_url)
        prediction_id = response['predictionID']
        result = get_prediction(prediction_id)
        return result, model_info
    except Exception as e:
        print(f"Error: {e}")

