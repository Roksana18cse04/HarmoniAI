from fastapi import APIRouter
from app.agents.content_creator_agent import generate_content_from_instruction

router= APIRouter()

@router.post("/content-creator")
async def content_creator_endpoint(instruction:str):
    
    response=generate_content_from_instruction(instruction)
    return response