
from typing import Optional
from pydantic import BaseModel

class VideoWithAudioRequest(BaseModel):
    text: Optional[str] = None,
    audio_url: Optional[str] = None,
    image_url: Optional[str] = None,
    image_prompt: Optional[str] = None