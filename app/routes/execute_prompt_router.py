from fastapi import APIRouter, File, UploadFile, Depends, Form
from typing import Optional
from app.agents.chaining_agent import run_multi_agent_chain
from app.schemas.input import InputRequest
router = APIRouter()

@router.post("/execute-prompt")
async def execute_prompt(prompt: str = Form(...), file: Optional[UploadFile] = File(default=None)):
    """
    Classify the given prompt into one of the predefined categories.
    """
    # Check if actual file was uploaded
    if file is None or not hasattr(file, 'filename') or not file.filename:
        file = None
    result = run_multi_agent_chain(prompt, file)
    
    return {"result": result}
    
    