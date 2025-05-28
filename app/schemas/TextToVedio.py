from pydantic import BaseModel
class TextToVideoRequest(BaseModel):
    prompt: str
    model_name: str
    duration: int