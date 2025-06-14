from app.services.voice_to_voice import create_voice_to_voice_prediction
from app.services._get_prediction import get_prediction



def voice_to_voice_clone_agents(model_name: str,input_text: str,audio_file_url: str,platform: str):
    # Get the prediction from the model
    try:
        # Create prediction
        result = create_voice_to_voice_prediction(model_name,input_text,audio_file_url,platform)
        prediction_id = result['prediction_id']
        price = result['price']
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        voice_clone_url = get_prediction(prediction_id)
        print(f"Output URL: {voice_clone_url['output']}")
        print(f"Processing time: {voice_clone_url ['metrics']['predict_time']}s")
        return {
            "voice_clone_url": voice_clone_url['output'],
            "price":price
        }
    except Exception as e:
        print(f"Error: {e}")