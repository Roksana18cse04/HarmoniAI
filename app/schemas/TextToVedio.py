from pydantic import BaseModel
from typing import Optional

class TextToVideoRequest(BaseModel):
    user_id:str
    chat_id:str
    prompt: str
    eachlabs_model_name: str
    duration: int
    intend :str

