from fastapi import APIRouter, Form
from typing import List
from app.agents.video_to_text_agent import video_to_text_generate

router = APIRouter()

@router.post("/video_to_text")
async def video_to_text(video_url: str = Form(...), intend: str = Form(...)):
    try:
        # video_bytes = await video_file.read()
        # video_r2_url = upload_to_r2(video_bytes, f"video/{video_file.filename}")
        # print(f"R2 Video URL: {video_r2_url}")

        result, model_info = video_to_text_generate(video_url)
        print(f"-------------routre-----------------")
        print(f"Generated Text: {result}")
        print(f"Model Info: {model_info}")
        return {
            "prompt": video_url,
            "response": result['output'],
            "price": result["metrics"]["cost"],
            "model_info": model_info,
            "runtime": result['metrics']['predict_time']
        }
    except Exception as e:
        return {"error": str(e)}
    
        
