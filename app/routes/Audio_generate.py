from fastapi import APIRouter, UploadFile, File, Form
from app.services.text_to_voice import text_to_audio_generate
from app.schemas.text_to_audio import TextToAudioRequest

router = APIRouter()

@router.post("/audio-generate")
async def audio_generate(prompt: str = Form(...)):
    result = text_to_audio_generate(prompt)
    return {
        "status": "success",
        "prompt": prompt,
        "result": result
    }