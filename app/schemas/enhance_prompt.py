from pydantic import BaseModel
class EnhanceRequest(BaseModel):
    platform: str
    base_prompt: str
    target_model: str
    intend: str


class EnhanceResponse(BaseModel):
    base_prompt: str
    target_model: str
    enhanced_prompt: str
    intend: str