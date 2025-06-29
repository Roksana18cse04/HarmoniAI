
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.agents.voice_cloning_agents import voice_to_voice_clone_agents
from app.utils.r2_uploader import upload_to_r2
import uuid
from app.routes.execute_prompt_router import get_history
from app.services.store_chat_message import store_generated_message

router = APIRouter()

@router.post("/voice-clone")
async def voice_cloning(
    chat_id: str = Form(...),
    audio_file: UploadFile = File(...),
    eachlabs_model_name: str = Form(...),
    llm_model: str = Form(...),
    prompt: str = Form(...),
    intend: str = Form(...),
):
    platform, full_prompt = get_history(chat_id, prompt)
    object_key = f"voice-clone-audio/{uuid.uuid4()}.wav"
    file_bytes = await audio_file.read()
    audio_file_url = upload_to_r2(file_bytes, object_key)

    result = voice_to_voice_clone_agents(platform, prompt, audio_file_url, llm_model, eachlabs_model_name, intend)
    if result is None:
        raise HTTPException(status_code=500, detail="Voice cloning failed.")

    response, model_info, llm_price = result
    lprice = llm_price['price']
    input_tokens = llm_price['input_token']
    output_tokens = llm_price['output_token']
    mprice = response['metrics']['cost']
    price = lprice + mprice

    # store_generated_message(user_id, chat_id, prompt, response=)
    return {
        "response": {
            'prompt': prompt,
            "status": response['status'],
            "result": response['output'],
            "price": price
        },
        "model_info": {
            'eachlabs_model_info': model_info,
            'llm_model_info': llm_model
        },
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "intend": intend,
        "runtime": round(response['metrics']['predict_time'], 3)
    }
