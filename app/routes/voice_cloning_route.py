from fastapi import APIRouter, UploadFile, File, Form
from app.agents.voice_cloning_agents import voice_to_voice_clone_agents
from app.utils.r2_uploader import upload_to_r2
import uuid

router = APIRouter()

@router.post("/voice-clone")
async def voice_cloning(
    platform: str = Form(...),
    audio_file: UploadFile = File(...),
    model_name: str = Form(...),
    prompt: str = Form(...),
    intend : str = Form(...),
):
    # Generate a unique object key using UUID
    object_key = f"voice-clone-audio/{uuid.uuid4()}.wav"

    file_bytes = await audio_file.read()
    audio_file_url = upload_to_r2(file_bytes, object_key)

    # Pass to agent
    response,model_info ,llm_price= voice_to_voice_clone_agents(model_name, prompt, audio_file_url,platform)

    lprice = llm_price['price']
    input_tokens = llm_price['input_token']
    output_tokens = llm_price['output_token']
    mprice=response['metrics']['cost']
    price = lprice+ response['metrics']['cost']
    print(f"Total price:--------{lprice} +{mprice} {price}")
    return {
        "response": {
            'prompt': prompt,
            "status": response['status'],
            "result": response['output'],
            "price":  price 
        },
        "model_info": model_info,
        "llm_price": lprice,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "intend": intend,
        "runtime": round( response['metrics']['predict_time'], 3)
    }
