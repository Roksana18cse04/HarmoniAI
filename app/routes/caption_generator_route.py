from fastapi import APIRouter, UploadFile, File, Form
from app.agents.image_caption_agent import generate_caption_from_image_and_instruction
from app.config import config
import shutil
import os

router= APIRouter()

@router.post("/caption-generator")
async def caption_generator_endpoint(
    file: UploadFile = File(...), 
    instruction:str = Form(...)
):  
    # Create path to save the file
    image_path = os.path.join(config.IMAGE_PATH, file.filename)

    # Ensure the directory exists
    os.makedirs(config.IMAGE_PATH, exist_ok=True)

    # Save the uploaded file to disk
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Generate caption
        response = generate_caption_from_image_and_instruction(image_path, instruction)
    finally:
        # Always delete the file, even if there's an error
        if os.path.exists(image_path):
            os.remove(image_path)
            
    return response