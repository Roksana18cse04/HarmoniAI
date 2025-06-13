from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.agents.pdf_to_text_extract_agents import pdf_to_text_extract
from app.utils.r2_uploader import upload_to_r2


router = APIRouter()
@router.post("/pdf_to_text")
async def pdf_to_text(file: UploadFile = File(...),intend:str=Form(...)):
    try:
        # Read the file
        contents = await file.read()
        object_key = file.filename
        url = upload_to_r2(contents,object_key)
        # Extract text from the file
        input_text = pdf_to_text_extract(url)
        text=" ".join(input_text.split())
        return JSONResponse(content={"text": text, "intend": intend}, media_type="application/json")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, media_type="application/json")
    
        
        