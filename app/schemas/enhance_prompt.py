from pydantic import BaseModel
class EnhanceRequest(BaseModel):
    platform: str
    base_prompt: str
    target_model: str
    intend: str
