from pydantic import BaseModel, Field

class TextToAudioRequest(BaseModel):
    platform: str
    model_name: str = Field(default="eleven-multilingual-v2")
    prompt: str
    intend: str
