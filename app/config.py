# app/config.py

import os


from pydantic import BaseModel

class ImageRequest(BaseModel):
    model_name: str
    prompt: str

class TextToVideoRequest(BaseModel):
    model_name: str
    prompt: str

class ImageToVideoRequest(BaseModel):       
    model_name: str
    prompt: str
    image_url: str


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "data.json")

