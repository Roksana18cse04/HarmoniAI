from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile

class ImageToImageRequest(BaseModel):
    model_name: str
    prompt: str
    style_slug: str
    image_url: Optional[str] = None  # For URL input option
    file: Optional[UploadFile] = None  # For file upload option
    
class ImageToImageResponse(BaseModel):
    prompt: str
    previous_image_url: Optional[str] = None
    new_image_url: Optional[str] = None
    status: Optional[str] = None
    prediction_id: Optional[str] = None
    error_message: Optional[str] = None