from fastapi import APIRouter, UploadFile, File, Form
from app.services.text_to_voice import text_to_audio_generate
from app.schemas.TextToAudio import TextToAudioRequest
from app.routes.execute_prompt_router import get_history
from app.routes.execute_prompt_router import get_history
from app.services.store_chat_message import store_generated_message
router = APIRouter()

@router.post("/text-audio-generate")
async def audio_generate(data:TextToAudioRequest):
    platform, full_prompt = get_history(data.chat_id, data.prompt)
    response,model_info,price_details = text_to_audio_generate(platform,data)
    mprice = response['metrics']['cost']
    lprice = price_details['price']
    total_price = lprice+mprice
    runtime=response['metrics']['predict_time']
    response={
        'status': response['status'],
        'output':response['output'],
        'price': total_price,
        'input_token': price_details['input_token'],
        'output_token': price_details['output_token']
    }
    llm_model_info={
        'name':data.llm_model_name,
        
    }
    store_generated_message(
        userId=data.user_id,
        chatId=data.chat_id,
        prompt=data.prompt,
        response=response,
        intend=data.intend,
        runtime=runtime,
        llm_model=llm_model_info,
        eachlabs_info=model_info
        
    )
    return {
        "response": {
            "prompt" : data.prompt,
            "status": response['status'],
            "result":response['output'],
            'price': total_price,  
        },
        "intend": data.intend,
        "model_info":{
            'eachlbs_model_info':model_info,
            'llm_model_info':llm_model_info,
            'input_token': price_details['input_token'],
            'output_token': price_details['output_token']
        },
        "runtime": runtime
    }