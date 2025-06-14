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
        result = text_to_video_generate(request)
        
        return {
            "message": "Video generated successfully",
            "prompt":prompt,
            "video_url": result
            
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
