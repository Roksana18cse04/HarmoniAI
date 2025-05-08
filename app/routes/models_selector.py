from fastapi import APIRouter
from app.agents.chaining_agent import run_multi_agent_chain


router = APIRouter()

@router.post("/fetch-models")
async def fetch_models(prompt: str):
    """
    Classify the given prompt into one of the predefined categories.
    """
    result = run_multi_agent_chain(prompt)
    return {"result": result}
    
    