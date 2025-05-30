from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.agents.dress_trail_agents import dress_trial_agent
from app.schemas.Image_To_Image import DressTrialImageRequest
from app.config import cloudinary
import cloudinary.uploader

router = APIRouter()



@router.post("/dress-trial-image-generate")
async def dress_trial_image_generate(
    cloth_image: UploadFile = File(...),
    human_image: UploadFile = File(...),
    intend : str = Form(...)
):
    cloth_image_bytes = await cloth_image.read()
    cloth_upload_result = cloudinary.uploader.upload(cloth_image_bytes, resource_type="image")
    
    human_image_bytes = await human_image.read()
    human_upload_result = cloudinary.uploader.upload(human_image_bytes, resource_type="image")

    cloth_image_url = cloth_upload_result["secure_url"]
    human_image_url = human_upload_result["secure_url"]
    print(f"Uploaded cloth image to Cloudinary: {cloth_image_url}")
    print(f"Uploaded human image to Cloudinary: {human_image_url}")
    
    data = DressTrialImageRequest(
        cloth_image_url=cloth_image_url,
        human_image_url=human_image_url
    )
    result = dress_trial_agent(data)

    return {
        "status": "success",
        "cloth_image_url": cloth_image_url,
        "human_image_url": human_image_url,
        "new_image_url": result.get("output")
    }
    