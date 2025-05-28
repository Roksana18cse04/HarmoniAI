from fastapi import APIRouter
from app.agents.chaining_agent import run_multi_agent_chain
from app.schemas.input import InputRequest
router = APIRouter()

@router.post("/execute-prompt")
async def execute_prompt(data: InputRequest):
    """
    Classify the given prompt into one of the predefined categories.
    """
    result = run_multi_agent_chain(data.prompt)
    return {"result": result}
    
    