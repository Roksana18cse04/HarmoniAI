
from typing import Optional
from pydantic import BaseModel

class VideoWithAudioRequest(BaseModel):
    user_id:str
    chat_id:str
    text: Optional[str] = None,
    audio_url: Optional[str] = None,
    image_url: Optional[str] = None,
    image_prompt: Optional[str] = None