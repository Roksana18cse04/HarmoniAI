from app.services.voice_to_voice import create_voice_to_voice_prediction
from app.services._get_prediction import get_prediction

def voice_to_voice_clone_agents(platform, prompt, audio_file_url, llm_model, eachlabs_name, intend):
    try:
        response, model_info, price_details = create_voice_to_voice_prediction(
            platform, prompt, audio_file_url, llm_model, eachlabs_name
        )
        prediction_id = response['predictionID']

        if not prediction_id:
            raise ValueError("Missing predictionID in response.")

        result = get_prediction(prediction_id)
        return result, model_info, price_details

    except Exception as e:
        print(f"Error: {e}")
        return None