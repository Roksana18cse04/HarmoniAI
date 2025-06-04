from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile
from app.enum.cat import Category  # assume you save Enum in enums folder

class ImageToImageRequest(BaseModel):
    model_name: str
    prompt: str
    style_slug: str
    reference_image: Optional[str] = None  # Change from image_url to reference_image
    file: Optional[UploadFile] = None
    
class ImageToImageResponse(BaseModel):
    prompt: str
    previous_image_url: Optional[str] = None
    new_image_url: Optional[str] = None
    status: Optional[str] = None
    prediction_id: Optional[str] = None
    error_message: Optional[str] = None
    
class DressTrialImageRequest(BaseModel):
    category: Category
    cloth_image_url: str
    mask_image_url: str
    human_image_url: str


