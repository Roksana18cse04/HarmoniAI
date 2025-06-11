from fastapi import APIRouter, UploadFile, File, Form
from app.agents.voice_cloning_agents import voice_to_voice_clone_agents
from app.utils.r2_uploader import upload_to_r2
import uuid

router = APIRouter()

@router.post("/voice-clone")
async def voice_cloning(
    platform: str = Form(...),
    audio_file: UploadFile = File(...),
    model_name: str = Form(...),
    prompt: str = Form(...)
):
    # Generate a unique object key using UUID
    object_key = f"voice-clone-audio/{uuid.uuid4()}.wav"

    file_bytes = await audio_file.read()
    audio_file_url = upload_to_r2(file_bytes, object_key)



    # Pass to agent
    result = voice_to_voice_clone_agents(model_name, prompt, audio_file_url,platform)
    print(result)

    return {
        "status": "success",
        "platform":platform,
        "prompt": prompt,
        "audio_file": audio_file_url,
        "result": result
    }
