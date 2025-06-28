# routes.py
from fastapi import APIRouter, Form
from app.schemas.enhance_prompt import EnhanceRequest
from app.services.enhance_prompt_generate import enhance_prompt
from app.routes.execute_prompt_router import get_history

enhance_router = APIRouter()
@enhance_router.post("/enhance-prompt/")
async def get_enhanced_prompt(request: EnhanceRequest):
    chat_id = request.chat_id
    base_prompt=request.base_prompt
    platform, full_prompt= get_history(chat_id, base_prompt)

    response = await enhance_prompt(
        platform,
        base_prompt,
        eachlabs_model = request.eachlabs_model,
        llm_model = request.llm_model,
        intend=request.intend
    )
    return response
