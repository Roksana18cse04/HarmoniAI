from pydantic import BaseModel
from typing import Optional

class TextToVideoRequest(BaseModel):
    prompt: str
    eachlabs_model_name: str
    duration: int
    intend :str

