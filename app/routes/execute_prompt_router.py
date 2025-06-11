from fastapi import APIRouter, File, UploadFile, Depends, Form
from typing import Optional, Union
from app.agents.chaining_agent import run_multi_agent_chain
from app.schemas.input import InputRequest
router = APIRouter()

@router.post("/execute-prompt")
async def execute_prompt(
    prompt: str = Form(...),
    file: Optional[Union[UploadFile, str]] = File(None)
):
    processed_file = None
    
    if file is not None:
        if isinstance(file, UploadFile) and file.filename:
            processed_file = file
        elif isinstance(file, str) and file.strip():
            # Handle string case - maybe it's a file path or base64?
            print(f"Received string instead of file: {file}")
            # You might want to convert string to UploadFile or handle differently
    
    result = run_multi_agent_chain(prompt, processed_file)
    return {"result": result}
    
    