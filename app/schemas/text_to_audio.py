from pydantic import BaseModel

class TextToAudioRequest(BaseModel):
    prompt:str
    model_name:str
