from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.utils import r2_uploader
from app.agents.image_to_image_process_agents import image_to_image_process

router = APIRouter()

@router.post("/image-to-process-images")
async def process_images(
    prompt: str = Form(...),
    image_files: List[UploadFile] = File(...),
    intend : str = Form(...),
):
    uploaded_image_urls = []

    for idx, image_file in enumerate(image_files):
        file_bytes = await image_file.read()
        file_extension = image_file.filename.split('.')[-1]
        object_key = f"uploads/input_image_{idx}.{file_extension}"

        try:
            uploaded_url = r2_uploader.upload_to_r2(file_bytes, object_key)
            uploaded_image_urls.append(uploaded_url)
        except Exception as e:
            return {"error": f"Failed to upload image at index {idx}: {str(e)}"}

    try:
        result = await image_to_image_process(prompt, uploaded_image_urls)
        return {
            "prompt": prompt,
            "input_images": {f"image_{i}": url for i, url in enumerate(uploaded_image_urls)},
            "result": result,
            "intend": intend
        }
    except Exception as e:
        return {"error": f"Image processing failed: {str(e)}"}
