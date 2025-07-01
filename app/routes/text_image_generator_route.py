from fastapi import APIRouter, UploadFile, File, Form,HTTPException
from fastapi.responses import JSONResponse
from app.agents.image_generator_agent import text_to_generate_image
from app.schemas.TextToImage import TextToImageRequest
from app.routes.execute_prompt_router import get_history
from app.services.store_chat_message import store_generated_message
import os
from dotenv import load_dotenv
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")

router = APIRouter()

@router.post("/text-image-generate")
def image_generate(data: TextToImageRequest):
    try:
        platform, full_prompt = get_history(data.chat_id, data.prompt)
        response, model_info = text_to_generate_image(data)
        intend = data.intend
        runtime = round(response['metrics']['predict_time'], 3)
        response_data = {
            "status": response['status'],
            "output": response['output'],
            "price": response['metrics']['cost']
        }

        store_generated_message(
            userId=data.user_id,
            chatId=data.chat_id,
            prompt=data.prompt,
            response=response_data,
            intend=intend,
            runtime=runtime,
            eachlabs_info=model_info
        )

        return {
            "response": {
                'prompt': data.prompt,
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
