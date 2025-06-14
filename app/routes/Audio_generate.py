from fastapi import APIRouter, UploadFile, File, Form
from app.services.text_to_voice import text_to_audio_generate
from app.schemas.TextToAudio import TextToAudioRequest

router = APIRouter()

@router.post("/text-audio-generate")
async def audio_generate(data:TextToAudioRequest):

    result = text_to_audio_generate(data)
    print(result)
    return result