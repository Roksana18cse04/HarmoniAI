from fastapi import APIRouter, Form
from typing import List
from app.agents.video_to_text_agent import video_to_text_generate

router = APIRouter()

@router.post("/video_to_text")
async def video_to_text(video_url: str = Form(...), intend: str = Form(...)):
    try:
        result, model_info = video_to_text_generate(video_url)
        return {
            "prompt": video_url,
            "response": result['output'],
            "price": result["metrics"]["cost"],
            "model_info": model_info,
            "runtime": result['metrics']['predict_time']
        }
    except Exception as e:
        return {"error": str(e)}
    
        
