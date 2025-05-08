# routes.py
from fastapi import APIRouter
from app.schemas.enhance_prompt import EnhanceRequest, EnhanceResponse
from app.services.enhance_prompt_generate import enhance_prompt

enhance_router = APIRouter()

@enhance_router.post("/enhance-prompt/", response_model=EnhanceResponse)
async def get_enhanced_prompt(request: EnhanceRequest) -> EnhanceResponse:
    """
    Handle the enhancement of a prompt.
    :param request: The request body containing base_prompt and target_model.
    :return: Enhanced prompt wrapped in EnhanceResponse.
    """
    base_prompt = request.base_prompt
    target_model = request.target_model
    
    # Get the enhanced prompt using the enhance_prompt function from basemodel.py
    enhanced_prompt = enhance_prompt(base_prompt, target_model)
    
    # Return the response using the EnhanceResponse Pydantic model
    return EnhanceResponse(
        status="success",
        base_prompt=base_prompt,
        target_model=target_model,
        enhanced_prompt=enhanced_prompt
    )
