from pydantic import BaseModel
class TextToVideoRequest(BaseModel):
    model_name: str
    prompt: str
    duration: int