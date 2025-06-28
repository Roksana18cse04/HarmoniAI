from app.services.voice_to_voice import create_voice_to_voice_prediction
from app.services._get_prediction import get_prediction



def voice_to_voice_clone_agents(model_name: str,input_text: str,audio_file_url: str,platform: str):
    # Get the prediction from the model
    try:
        # Create prediction
        input_text = str(input_text).strip()
        response ,price_details= create_voice_to_voice_prediction(model_name,input_text,audio_file_url,platform)
        prediction_id = response['predictionID']    
        # Get result
        result = get_prediction(prediction_id)
        return result, response ,price_details
    except Exception as e:
        print(f"Error: {e}")
        
