from fastapi import APIRouter, UploadFile, File
from app.utils.r2_uploader import upload_to_r2
from app.agents.audio_video import generate_video_with_audio
from app.schemas.video_with_audio import VideoWithAudioRequest

router = APIRouter()

@router.post("/video-generate")
async def video_generate(
    image_file: UploadFile = File(...),
    audio_file: UploadFile = File(...)
):
    # Read file bytes
    image_bytes = await image_file.read()
    audio_bytes = await audio_file.read()

    # Define object keys (paths in bucket)
    image_key = f"images/{image_file.filename}"
    audio_key = f"audio/{audio_file.filename}"

    # Upload to R2 using your function
    image_url = upload_to_r2(image_bytes, image_key)
    audio_url = upload_to_r2(audio_bytes, audio_key)

    if not image_url or not audio_url:
        return {"error": "Upload failed"}

    # Use uploaded URLs to generate video
    request_data = VideoWithAudioRequest(image_url=image_url, audio_url=audio_url)
    video_url = generate_video_with_audio(data=request_data)

    return {
        "image_url": image_url,
        "audio_url": audio_url,
        "video_url": video_url
    }
