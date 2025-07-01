from fastapi import APIRouter, UploadFile, File,Form,HTTPException
from app.utils.r2_uploader import upload_to_r2
from app.agents.audio_video import generate_video_with_audio
from app.routes.execute_prompt_router import get_history
from app.services.store_chat_message import store_generated_message

router = APIRouter()

@router.post("/image-video-generate")
async def video_generate(
    user_id: str=Form(...),
    chat_id:str=Form(...),  
    prompt:str=Form(...), 
    image_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    intend : str=Form(...)
):
    try:
        platform, full_prompt = get_history(chat_id, prompt)
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
        response,model_info = generate_video_with_audio(audio_url, image_url)
        
        runtime = round(response['metrics']['predict_time'], 3)
        response_data = {
            "status": response['status'],
            "output": response['output'],
            "price": response['metrics']['cost']
        }
        input_urls = f"{image_url}\n{audio_url}"

        store_generated_message(
            userId=user_id,
            chatId=chat_id,
            prompt=prompt,
            response=response_data,
            intend=intend,
            runtime=runtime,
            input_urls=input_urls,
            eachlabs_info=model_info
        )

        return {
            "response": {
                'prompt': prompt,
                "status": response['status'],
                "result": response['output'],
                "price": response['metrics']['cost']
            },
            "model_info": {
                'eachlabs_model_info': model_info,
            },
            "intend": intend,
            "runtime": runtime
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
    