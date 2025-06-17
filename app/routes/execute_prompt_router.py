from fastapi import APIRouter, File, UploadFile, Depends, Form
from typing import Optional, Union
from app.agents.chaining_agent import run_multi_agent_chain
from app.services.correct_symspell import correct_spelling
from app.schemas.input import InputRequest
import requests
router = APIRouter()

def get_history(chatId, prompt):
    api_url = f"https://harmoniai-backend.onrender.com/api/v1/conversations/{chatId}"
    token= "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2ODRhNzZiMzM3MjEzYzA0ODExNjQ0MmQiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3NTAwNDI3MzksImV4cCI6MTgzNjQ0MjczOX0.23FDVEKnEE3bvgD-CRjvV1apGuqNtsZnecCbf3g9uA4"
    headers= {
        "Authorization": token
    }
    res = requests.get(api_url, headers=headers)
    res.raise_for_status()
    data = res.json()
    # Step 1: Extract chat history
    chat_history = data['data']['chat']
    platform = data['data']['platform']
    history_messages = []

    for chat in chat_history:
        for p in chat.get("prompt", []):
            if p["type"] == "text":
                history_messages.append(f"User: {p['content']}")
        for r in chat.get("response", []):
            if r["type"] == "text":
                history_messages.append(f"Assistant: {r['content']}")

    # Step 2: Combine history with current prompt
    history_text = "\n".join(history_messages)
    full_prompt = f"{history_text}\nUser: {prompt}\nAssistant:"
    return platform, full_prompt

@router.post("/execute-prompt")
async def execute_prompt(
    chat_id: str = Form(...),
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

    prompt= correct_spelling(prompt)
    platform, full_prompt= get_history(chat_id, prompt)        
    
    result = run_multi_agent_chain(platform, prompt, full_prompt, processed_file)
    return {"result": result}
    
    