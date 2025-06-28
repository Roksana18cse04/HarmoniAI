from pydantic import BaseModel, Field

class TextToAudioRequest(BaseModel):
    chat_id : str
    llm_model_name:str
    eachlabs_model_name: str = Field(default="eleven-multilingual-v2")
    prompt: str
    intend: str
