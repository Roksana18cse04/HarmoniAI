from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.agents.pdf_to_text_extract_agents import pdf_to_text_extract
from app.utils.r2_uploader import upload_to_r2
import re

router = APIRouter()
@router.post("/pdf_to_text")
async def pdf_to_text(file: UploadFile = File(...), intend: str = Form(...)):
    try:
        contents = await file.read()
        object_key = file.filename
        url = upload_to_r2(contents, object_key)
        response, model_info = pdf_to_text_extract(url)
        cleaned_output = re.sub(r'\s+', ' ', response['output'].replace('\n\n', ' ').replace('\n', ' ')).strip()

        return {
            "response": {
                'prompt': url,
                "status": response['status'],
                "result": cleaned_output,
                "price": round(response['metrics']['cost'], 4)
            },
            "model_info": model_info,
            "intend": intend,
            "runtime": round( response['metrics']['predict_time'], 3)
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "An error occurred while processing the PDF file."})