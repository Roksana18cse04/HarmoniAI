from fastapi import APIRouter, UploadFile, File, Form
from app.services.text_to_voice import text_to_audio_generate

router = APIRouter()

@router.post("/text-audio-generate")
async def audio_generate(platform :str = Form(...),prompt: str = Form(...),intend:str=Form(...)):

    result = text_to_audio_generate(prompt)
    print(result)
    return {
        "status": "success",
        "platform":platform,
        "prompt": prompt,
        "result": result,
        "intend": intend
    }