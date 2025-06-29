from pydantic import BaseModel

class TextToImageRequest(BaseModel):
    user_id:str
    chat_id:str
    eachlabs_model_name: str
    prompt: str
    intend: str
    