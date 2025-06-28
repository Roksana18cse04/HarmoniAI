import os
from app.services.video_to_text import get_prediction,create_prediction


def video_to_text_generate(video_url:str):
    # Create a new prediction
    try:
    # Create prediction
        response = create_prediction(video_url)
        print(f"Prediction response: {response}")
        prediction_id = response['prediction_id']
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        model_info = response['model_info']
        print(f"Model Info: {model_info}")
        print(f"---------------------------------")
        result = get_prediction(prediction_id)
        
        print(f"Prediction result:---------- {result}")
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result, response['model_info']
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Example input
    video_url = "https://cdn.harmoniai.net/video/screen-capture.webm"

    # Generate text from video and get result
    result, model_info = video_to_text_generate(video_url)
    print(f"Generated Text: {result}")
    print(f"Model Info: {model_info}")