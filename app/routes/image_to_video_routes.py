from fastapi import APIRouter, UploadFile, File,Form
from app.utils.r2_uploader import upload_to_r2
from app.agents.audio_video import generate_video_with_audio

router = APIRouter()

@router.post("/image-video-generate")
async def video_generate(
    image_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    intend : str=Form(...)
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
    result,model_info = generate_video_with_audio(audio_url, image_url)
    
    print(f"Generated Video URL: {result}")
    print(f"Model Info: {model_info}")

    return {
        "prompt": {
            "image_url": image_url,
            "audio_url": audio_url,
        },
        "response": result['output'],
        "price": result["metrics"]["cost"],
        "model_info": model_info,
        "intend": intend,
        "runtime": result['metrics']['predict_time']
    }
