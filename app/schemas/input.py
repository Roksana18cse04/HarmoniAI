from pydantic import BaseModel

class InputRequest(BaseModel):
    prompt:str
    