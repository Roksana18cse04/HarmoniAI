# app/routes/video_routes.py
from fastapi import APIRouter, HTTPException, Form
from app.schemas.TextToVedio import TextToVideoRequest
from app.agents.vedio_generator_agent import text_to_video_generate
from app.routes.execute_prompt_router import get_history
from app.services.store_chat_message import store_generated_message
router = APIRouter()

@router.post("/text-to-generate-video/")
async def generate_video(request: TextToVideoRequest):
    try:
        print(f"--------hi__________")
        #platform, full_prompt = get_history(request.chat_id, request.prompt)
        prompt = request.prompt
        
        response,model_info,intend = text_to_video_generate(request)
        print(f"-----------------",response)
        response={
            "status": response['status'],
            "result": response['output'],
            "price": response['metrics']['cost']
        }
        runtime = round( response['metrics']['predict_time'], 3)
        
        store_generated_message(
            userId=request.user_id, 
            chatId=request.chat_id, 
            prompt=prompt, 
            response=response, 
            intend=intend, 
            runtime=runtime,
            eachlabs_info=model_info
        )
        
        return {
        "response": {
            'prompt': prompt,
            "status": response['status'],
            "result": response['output'],
            "price": response['metrics']['cost']
        },
        "model_info": {
                'eachlabs_model_info': model_info,
        },
        "intend": intend,
        "runtime": runtime
    }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
