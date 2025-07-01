from pydantic import BaseModel
class EnhanceRequest(BaseModel):
    user_id:str
    chat_id:str
    base_prompt: str
    eachlabs_model: str
    llm_model: str
    intend: str
