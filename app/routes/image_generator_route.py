from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.agents.image_generator_agent import text_to_generate_image
from app.agents.image_to_image_generate_agents import image_to_generate_image
from app.schemas.TextToImage import TextToImageRequest
from app.schemas.Image_To_Image import ImageToImageRequest, ImageToImageResponse
from app.config import cloudinary
import cloudinary.uploader

router = APIRouter()

@router.post("/image-generate")
async def image_generate(data: TextToImageRequest):
    """
    Classify the given prompt into one of the predefined categories.
    """
    result = text_to_generate_image(data)
    return {"result": result}

@router.post("/image-to-image-generate", response_model=ImageToImageResponse)
async def image_to_image_generate(
    model_name: str = Form(...),
    style: str = Form(...),
    prompt: str = Form(""),
    file: UploadFile = File(...)
):
    image_bytes = await file.read()
    upload_result = cloudinary.uploader.upload(image_bytes, resource_type="image")
    image_url = upload_result["secure_url"]
    print(f"Uploaded image to Cloudinary: {image_url}")
    # Extract the secure URL from the upload response

    data = ImageToImageRequest(
    model_name=model_name,
    prompt=prompt,
    style_slug=style,
    reference_image=image_url  # Change from image_url=image_url
)
    result = image_to_generate_image(data)
    if result is None:
        return ImageToImageResponse(
            prompt=prompt,
            previous_image_url=image_url,
            new_image_url=None,
            status="error",
            prediction_id=None,
            error_message="Image generation failed"
        )
    # Return the response with prompt, previous_image_url (Cloudinary), and new_image_url (Eachlabs AI)
    return ImageToImageResponse(
        prompt=prompt,
        previous_image_url=image_url,  # Cloudinary URL
        new_image_url=result.get("output"),  # Eachlabs AI generated URL
        status=result.get("status"),
        prediction_id=result.get("prediction_id"),
        error_message=result.get("error_message")
    )
