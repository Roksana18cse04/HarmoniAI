from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.agents.image_generator_agent import text_to_generate_image
from app.schemas.TextToImage import TextToImageRequest

router = APIRouter()

@router.post("/text-image-generate")
async def image_generate(data: TextToImageRequest):
    """
    Classify the given prompt into one of the predefined categories.
    """
    result = text_to_generate_image(data)
    return result

