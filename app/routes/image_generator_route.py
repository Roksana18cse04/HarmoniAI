from fastapi import APIRouter
from app.agents.image_generator_agent import imageGenerate
from app.schemas.TextToImage import TextToImageRequest

router = APIRouter()

@router.post("/image-generate")
async def image_generate(data: TextToImageRequest):
    """
    Classify the given prompt into one of the predefined categories.
    """
    result = imageGenerate(data)
    return {"result": result}