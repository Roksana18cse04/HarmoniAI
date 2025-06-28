from pydantic import BaseModel

class TextToImageRequest(BaseModel):
    eachlabs_model_name: str
    prompt: str
    intend: str
    