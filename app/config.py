# app/config.py

import os


from pydantic import BaseModel

class ImageRequest(BaseModel):
    model_name: str
    prompt: str

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "data.json")

