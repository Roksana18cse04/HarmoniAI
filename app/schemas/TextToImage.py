from pydantic import BaseModel

class TextToImageRequest(BaseModel):
    model_name: str
    prompt: str