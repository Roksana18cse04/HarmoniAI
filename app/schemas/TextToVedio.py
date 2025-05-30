from pydantic import BaseModel
from typing import Optional

class TextToVideoRequest(BaseModel):
    prompt: str
    model_name: str
    duration: int

