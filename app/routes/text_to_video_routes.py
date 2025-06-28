# app/routes/video_routes.py

from fastapi import APIRouter, HTTPException, Form
from app.schemas.TextToVedio import TextToVideoRequest
from app.agents.vedio_generator_agent import text_to_video_generate

router = APIRouter()

@router.post("/text-to-generate-video/")
async def generate_video(request: TextToVideoRequest):
    """
    Generate a video from a given prompt using EachLabs API.
    """
    try:
        prompt = request.prompt
        response,model_info,intend = text_to_video_generate(request)
        
        return {
        "response": {
            'prompt': prompt,
            "status": response['status'],
            "result": response['output'],
            "price": response['metrics']['cost']
        },
        "model_info": model_info,
        "intend": intend,
        "runtime": round( response['metrics']['predict_time'], 3)
    }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
