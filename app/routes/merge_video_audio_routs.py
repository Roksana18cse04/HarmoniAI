from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.config import AUDIO_DIR, VIDEO_DIR,OUTPUT_DIR_VIDEO
from app.services.merge_audio_video import merge_audio_video
import os
from app.config import cloudinary
import cloudinary.uploader

router = APIRouter()


@router.post("/merge-audio-video")
async def merge_audio_video(audio_file: UploadFile = File(...), video_file: UploadFile = File(...)):
    
    # Upload the audio file to Cloudinary
    audio_bytes= await audio_file.read()
    audio_upload = cloudinary.uploader.upload(audio_bytes, resource_type="raw")
    audio_url = audio_upload["secure_url"]
    print(f"audio_url : {audio_url}")
    
    video_bytes= await video_file.read()
    video_upload = cloudinary.uploader.upload(video_bytes, resource_type="raw")
    video_url = video_upload["secure_url"]
    print(f"Video_url : {video_url}")
    
    # audio video path setup
    audio_path = os.path.join(AUDIO_DIR, audio_file.filename)
    video_path = os.path.join(VIDEO_DIR, video_file.filename)

    with open(audio_path, "wb") as f:
        f.write(await audio_file.read())
    with open(video_path, "wb") as f:
        f.write(await video_file.read())


    output_path = os.path.join(OUTPUT_DIR_VIDEO, video_file.filename)
    
    output_video_path = merge_audio_video(audio_path, video_path, output_path)
    print(f"Output_path : {output_video_path}")
    try:
        # Upload the output video to Cloudinary
        output_video_bytes = open(output_video_path, "rb").read()
        output_video_upload = cloudinary.uploader.upload(output_video_bytes, resource_type="raw")
        output_video_url = output_video_upload["secure_url"]
        print(f"Output_video_url : {output_video_url}")
        return {
            "message": "Audio and video merged successfully",
            "base_audio_url": audio_url,
            "base_video_url": video_url,
            "output_video_path": output_video_path,
            "output_video_url": output_video_url      
        }
    
    except Exception as e:
        print(f"Error: {e}")
    
    
    