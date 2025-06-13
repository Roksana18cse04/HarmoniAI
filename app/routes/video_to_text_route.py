from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.utils.r2_uploader import upload_to_r2
from app.agents.video_to_text_agent import video_to_text_generate

router = APIRouter()

@router.post("/video_to_text")
async def video_to_text(video_file: UploadFile = File(...),intend:str=Form(...)):
    try:
        video_bytes = await video_file.read()
        video_r2_url = upload_to_r2(video_bytes, f"video/{video_file.filename}")
        print(f"R2 Video URL: {video_r2_url}")

        result = video_to_text_generate(video_r2_url)
        return {
            "prompt" : video_r2_url,
            "result": result ,
            "intend": intend
        }
    except Exception as e:
        return {"error": str(e)}
    
        
