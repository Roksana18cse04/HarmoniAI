from pydantic import BaseModel
from fastapi import Form

class InputRequest(BaseModel):
    prompt:str = Form(...)
    
    