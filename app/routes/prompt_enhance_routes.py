# routes.py
from fastapi import APIRouter, Form
from app.schemas.enhance_prompt import EnhanceRequest
from app.services.enhance_prompt_generate import enhance_prompt
from app.routes.execute_prompt_router import get_history
from app.services.store_chat_message import store_generated_message
import mimetypes
import time

enhance_router = APIRouter()
@enhance_router.post("/enhance-prompt/")
async def get_enhanced_prompt(request: EnhanceRequest):
    start_time = time.time()
    chat_id = request.chat_id
    base_prompt=request.base_prompt
    platform, full_prompt= get_history(chat_id, base_prompt)
    
    result,price= await enhance_prompt(
        platform,
        base_prompt,
        eachlabs_model = request.eachlabs_model,
        llm_model = request.llm_model,
        intend=request.intend
    )
    runtime = round(time.time() - start_time, 3)
    response={
        "status":"sucess",
        "output":result,
        "price":price["price"],
        "input_token":price['input_token'],
        "output_token":price['output_token']
    }
    store_generated_message(
        userId=request.user_id, 
        chatId=chat_id, 
        prompt=request.base_prompt, 
        response=response, 
        intend=request.intend, 
        runtime=runtime,
        llm_model=request.llm_model
        )

    return {
        "status":response["status"],
        "input":base_prompt,
        "result":result,
        "price":price["price"],
        "llm_model_info":{
            "llm_model":request.llm_model,
            "input_token":price['input_token'],
            "output_token":price['output_token']
        },
        "runtime":runtime,
        "intend":request.intend
    }
