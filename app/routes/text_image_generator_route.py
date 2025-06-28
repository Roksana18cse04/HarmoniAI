from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.agents.image_generator_agent import text_to_generate_image
from app.schemas.TextToImage import TextToImageRequest
import os
from dotenv import load_dotenv
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")

router = APIRouter()

@router.post("/text-image-generate")
def image_generate(data: TextToImageRequest):
    """
    Classify the given prompt into one of the predefined categories.
    """
    response, model_info = text_to_generate_image(data)
    intend = data.intend
    return {
        "response": {
            "prompt": data.prompt,
            "status": response['status'],
            "result": response['output'],
            "price": response['metrics']['cost'],
        },
        "model_info": model_info,
        "intend": intend,
        "runtime": round( response['metrics']['predict_time'], 3)
    }