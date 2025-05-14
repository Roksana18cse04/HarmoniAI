from fastapi import APIRouter, UploadFile, File
import os
import cloudinary
import cloudinary.uploader
from app.agents.audio_video import generate_video_with_audio
from app.schemas.video_with_audio import VideoWithAudioRequest


router = APIRouter()
@router.post("/video-generate")
async def video_generate(image_file: UploadFile = File(...),audio_file: UploadFile = File(...)):
    """
    Uploads an image and audio file to Cloudinary and returns their URLs.
    """

    
    # Upload to Cloudinary
    image_bytes = await image_file.read()
    audio_bytes = await audio_file.read()
    image_upload = cloudinary.uploader.upload(image_bytes, resource_type="image")
    audio_upload = cloudinary.uploader.upload(audio_bytes, resource_type="auto")
    image_url = image_upload.get("secure_url")
    audio_url = audio_upload.get("secure_url")
    print(f"Uploaded image to Cloudinary: {image_url}")
    print(f"Uploaded audio to Cloudinary: {audio_url}")
    
    request_data = VideoWithAudioRequest(image_url=image_url, audio_url=audio_url)
    video_url = generate_video_with_audio(data=request_data)
    print(f"Generated video URL: {video_url}")
    
    return {
        "image_url": image_url,
        "audio_url": audio_url,
        "video_url": video_url
    }

