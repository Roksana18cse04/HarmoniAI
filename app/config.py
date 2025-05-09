# app/config.py

import cloudinary
import os
from pydantic import BaseModel
class ImageToVideoRequest(BaseModel):       
    model_name: str
    prompt: str
    image_url: str


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "data.json")


# Configure Cloudinary
cloudinary.config(
    cloud_name="dhubxnqvq",
    api_key="191483941177317",
    api_secret="_UxT7j99p2LnLZwAHznk4HlSFnw"
)