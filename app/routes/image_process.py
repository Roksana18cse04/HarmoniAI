from fastapi import APIRouter, UploadFile, File, Form
from typing import List

router = APIRouter()

@router.post("/process-images")
async def process_images(
    prompt: str = Form(...),
    files: List[UploadFile] = File(...)
):
    pass