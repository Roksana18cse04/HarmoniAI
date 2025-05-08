from pydantic import BaseModel
class EnhanceRequest(BaseModel):
    base_prompt: str
    target_model: str

class EnhanceResponse(BaseModel):
    status: str
    base_prompt: str
    target_model: str
    enhanced_prompt: str