from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.utils import r2_uploader
from app.agents.image_to_image_process_agents import image_to_image_process
from app.routes.execute_prompt_router import get_history
from app.services.store_chat_message import store_generated_message

router = APIRouter()

@router.post("/image-to-process-images")
async def process_images(
    user_id:str = Form(...),
    chat_id:str = Form(...),
    llm_model:str =Form(...),
    prompt: str = Form(...),
    image_files: List[UploadFile] = File(...),
    intend : str = Form(...),
):
    try:
        platform, _ = get_history(chat_id, prompt)
    except Exception as e:
        return {"error": f"Failed to get history: {str(e)}"}
    uploaded_image_urls = []

    for idx, image_file in enumerate(image_files):
        file_bytes =await image_file.read()
        file_extension = image_file.filename.split('.')[-1]
        object_key = f"uploads/input_image_{idx}.{file_extension}"

        try:
            uploaded_url = r2_uploader.upload_to_r2(file_bytes, object_key)
            uploaded_image_urls.append(uploaded_url)
        except Exception as e:
            return {"error": f"Failed to upload image at index {idx}: {str(e)}"}

    try:
        result_data, model_metadata,llm_price=image_to_image_process(prompt, uploaded_image_urls,platform,llm_model)
        
        input_token = llm_price['input_token']
        output_token = llm_price['input_token']
        l_price = llm_price['price']
        emodel_price = result_data['metrics']['cost']
        total_price = l_price+emodel_price
        runtime = result_data['metrics']['predict_time']
        status = result_data['status']
        output = result_data['output']

        eachlabs_info = model_metadata

        response={
            "status": status,
            "output": output,
            "price": total_price,
            "input_token": input_token,
            "output_token": output_token,
            
        }
        print("-------------hello")
        store_generated_message(
            userId=user_id, 
            chatId=chat_id, 
            prompt=prompt, 
            response=response, 
            intend=intend, 
            runtime=runtime,
            input_urls=uploaded_image_urls,
            eachlabs_info=eachlabs_info,
            llm_model=llm_model
        )
        print(f"----------hello--------------")
        return {
            'input':{
                "prompt":prompt,
                "input_urls":uploaded_image_urls,
            },
            'response':{
                'status':result_data['status'],
                'result':result_data['output'],
                'price': total_price  
            },
            'model_info':{
                'eachlabs_model_info':model_metadata,
                'llm_model_info':{
                    'llm_model':llm_model,
                    'input_token':input_token,
                    'output_token':output_token,
                }
            },
            "intend": intend,
            "runtime": runtime
        }
    except Exception as e:
        return {"error": f"Image processing failed: {str(e)}"}
