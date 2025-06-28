import requests
import time
import os
from app.services.video_generation import create_prediction 
from app.services._get_prediction import get_prediction
from app.schemas.TextToVedio import TextToVideoRequest
from dotenv import load_dotenv
load_dotenv(override=True)
 
API_KEY =  os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def text_to_video_generate(data:TextToVideoRequest):
    try:
        response,model_info = create_prediction( data.prompt, data.eachlabs_model_name, data.duration)
        prediction_id = response["predictionID"]
        
        result = get_prediction(prediction_id)
        intend = data.intend
        url = result['output']
        if url:
            return result,model_info,intend
        else:
            raise Exception("Video generation failed: No output URL found.")
    except Exception as e:
        print(f"Error while fetching prediction: {e}")
        raise
