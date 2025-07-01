from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.agents.pdf_to_text_extract_agents import pdf_to_text_extract
from app.utils.r2_uploader import upload_to_r2
from app.routes.execute_prompt_router import get_history
from app.services.store_chat_message import store_generated_message
import re

router = APIRouter()
@router.post("/pdf_to_text")
async def pdf_to_text(
    user_id: str=Form(...),
    chat_id:str=Form(...),  
    prompt:str=Form(...), 
    file: UploadFile = File(...), 
    intend: str = Form(...)
):
    try:
        platform, full_prompt = get_history(chat_id, prompt)
        contents = await file.read()
        object_key = file.filename
        pdf_url = upload_to_r2(contents, object_key)
        result_data, model_info = pdf_to_text_extract(pdf_url)
        cleaned_output = re.sub(r'\s+', ' ', result_data['output'].replace('\n\n', ' ').replace('\n', ' ')).strip()

        emodel_price = result_data['metrics']['cost']
        runtime = result_data['metrics']['predict_time']
        status = result_data['status']
        
        response={
            "status": status,
            "output": cleaned_output,
            "price": emodel_price,            
        }
        store_generated_message(
            userId=user_id, 
            chatId=chat_id, 
            prompt=prompt, 
            response=response, 
            intend=intend, 
            runtime=runtime,
            input_urls=pdf_url,
            eachlabs_info=model_info
        )
        return {
            "input": {
                "prompt": prompt,
                "video_url": pdf_url
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