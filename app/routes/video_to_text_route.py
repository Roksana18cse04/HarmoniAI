from fastapi import APIRouter, Form
from typing import List
from app.agents.video_to_text_agent import video_to_text_generate
from app.routes.execute_prompt_router import get_history
from app.services.store_chat_message import store_generated_message

router = APIRouter()

@router.post("/video_to_text")
async def video_to_text(
    user_id: str = Form(...),
    chat_id: str = Form(...),
    video_url: str = Form(...),
    prompt: str = Form(...),
    intend: str = Form(...)
):
    try:
        platform, full_prompt = get_history(chat_id, prompt)
        result_data, model_info = video_to_text_generate(video_url)

        
        emodel_price = result_data['metrics']['cost']
        runtime = result_data['metrics']['predict_time']
        
        status = result_data['status']
        output = result_data['output']
        
        eachlabs_info = model_info

        response={
            "status": status,
            "output": output,
            "price": emodel_price,            
        }
        print(f"---------------hi----------------")
        # store_generated_message(user_id, chat_id, prompt, response=)
        store_generated_message(
            userId=user_id, 
            chatId=chat_id, 
            prompt=prompt, 
            response=response, 
            intend=intend, 
            runtime=runtime,
            eachlabs_info=eachlabs_info
        )
        return {
            "input": {
                "prompt": prompt,
                "video_url": video_url
            },
            "response": result_data['output'],
            "price": result_data["metrics"]["cost"],
            "model_info": {
                'eachlabs_model_info': model_info,
            
            },
            "runtime": result_data['metrics']['predict_time']
        }
    except Exception as e:
        return {"error": str(e)}
    
        
