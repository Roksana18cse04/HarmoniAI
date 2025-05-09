from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.agents.image_generator_agent import text_to_generate_image
from app.agents.image_to_image_generate_agents import image_to_generate_image
from app.schemas.TextToImage import TextToImageRequest
from app.schemas.Image_To_Image import ImageToImageRequest, ImageToImageResponse
from app.services.UploadFile import upload_image_to_cloudinary


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
    contents = await file.read()
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)
    image_url = upload_image_to_cloudinary(temp_path, folder="image")
    import os
    os.remove(temp_path)

    data = ImageToImageRequest(
        model_name=model_name,
        prompt=prompt,
        style_slug=style,  # schema uses style_slug, API expects 'style'
        image_url=image_url
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
