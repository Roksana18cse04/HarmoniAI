from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from app.config import AUDIO_DIR, VIDEO_DIR, OUTPUT_DIR_VIDEO
from app.services.merge_audio_video import merge_audio_video
from app.utils.r2_uploader import upload_to_r2
import os

router = APIRouter()

@router.post("/merge-audio-video")
async def merge_audio_video_route(audio_file: UploadFile = File(...), video_file: UploadFile = File(...)):
    # Read and upload audio
    audio_bytes = await audio_file.read()
    audio_r2_url = upload_to_r2(audio_bytes, f"audio/{audio_file.filename}")
    print(f"R2 Audio URL: {audio_r2_url}")

    # Read and upload video
    video_bytes = await video_file.read()
    video_r2_url = upload_to_r2(video_bytes, f"video/{video_file.filename}")
    print(f"R2 Video URL: {video_r2_url}")

    # Save files locally for merging
    audio_path = os.path.join(AUDIO_DIR, audio_file.filename)
    video_path = os.path.join(VIDEO_DIR, video_file.filename)

    with open(audio_path, "wb") as f:
        f.write(audio_bytes)
    with open(video_path, "wb") as f:
        f.write(video_bytes)

    # Merge audio and video
    output_path = os.path.join(OUTPUT_DIR_VIDEO, video_file.filename)
    output_video_path = merge_audio_video(audio_path, video_path, output_path)

    try:
        with open(output_video_path, "rb") as f:
            output_bytes = f.read()
        output_video_r2_url = upload_to_r2(output_bytes, f"output/{video_file.filename}")
        print(f"Output Video R2 URL: {output_video_r2_url}")
        os.remove(audio_path)
        os.remove(video_path)
        os.remove(output_video_path)

        return {
            "message": "Audio and video merged successfully",
            "base_audio_url": audio_r2_url,
            "base_video_url": video_r2_url,
            "output_video_path": output_path,
            "output_video_url": output_video_r2_url
        }

    except Exception as e:
        print(f"Upload Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
