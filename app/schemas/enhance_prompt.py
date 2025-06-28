from pydantic import BaseModel
class EnhanceRequest(BaseModel):
    chat_id: str
    base_prompt: str
    eachlabs_model: str
    llm_model: str
    intend: str
