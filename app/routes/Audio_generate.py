from fastapi import APIRouter, UploadFile, File, Form
from app.services.text_to_voice import text_to_audio_generate
from app.schemas.TextToAudio import TextToAudioRequest
from app.routes.execute_prompt_router import get_history

router = APIRouter()

@router.post("/text-audio-generate")
async def audio_generate(data:TextToAudioRequest):
    platform, full_prompt = get_history(data.chat_id, data.prompt)
    response,model_info,price_details = text_to_audio_generate(platform,data)
    mprice = response['metrics']['cost']
    lprice = price_details['price']
    total_price = lprice+mprice
    
    return {
        "response": {
            "prompt" : data.prompt,
            "status": response['status'],
            "result":response['output'],
            'price': total_price,  
        },
        "intend": data.intend,
        "model_info":model_info,
        "runtime": response['metrics']['predict_time']
    }