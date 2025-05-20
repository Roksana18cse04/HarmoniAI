from fastapi import APIRouter
from app.agents.content_creator_agent import generate_content_from_instruction
from app.schemas.input import InputRequest

router= APIRouter()

@router.post("/content-creator")
async def content_creator_endpoint(data: InputRequest):
    
    response=generate_content_from_instruction(data.prompt)
    return response