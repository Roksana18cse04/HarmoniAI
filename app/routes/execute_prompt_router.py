from fastapi import Request, APIRouter, File, UploadFile, Form
from typing import Optional, Union, List
from app.agents.chaining_agent import run_multi_agent_chain
from app.services.correct_symspell import correct_spelling
from app.schemas.input import InputRequest
from app.utils.r2_uploader import upload_to_r2
import uuid
import requests
import mimetypes

from app.services.token_manager import TokenManager, convert_dollar_into_token

router = APIRouter()

def get_history(chatId, prompt):
    print("call get_history---------------")
    api_url = f"https://harmoniai-backend.onrender.com/api/v1/conversations/{chatId}?limit=10"
    res = requests.get(api_url)
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

# ----------------update user token--------------------
def update_user_token(user_id, auth_token, cost):
    used_token = convert_dollar_into_token(cost)
    print("used token----------------------", used_token)
    api_url = f"https://harmoniai-backend.onrender.com/api/v1/users/update-token/{user_id}"
    headers = {
        "Authorization": auth_token
    }
    payload = {
        "token": used_token
    }
    try:
        response = requests.put(api_url, headers=headers, json=payload)
        response.raise_for_status()
        return {
            "success": True,
            "message": "Token updated successfully"
        }
    except requests.exceptions.RequestException as e:
        print("Error updating user token:", e)
        return {
            "success": False,
            "message": str(e)
        }

@router.post("/execute-prompt")
async def execute_prompt(
    request:Request,
    user_id: str = Form(...), 
    chat_id: str = Form(...),
    model: str = Form(...),
    prompt: str = Form(...),
    youtube_url: Optional[str] = Form(None),  # <-- YouTube URL comes from a separate form field
    files: Optional[List[Union[UploadFile, str]]] = File(None)  # Multiple uploaded files 
):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return {"error": "Authorization header missing"}

    if auth_header.startswith("Bearer "):
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = auth_header  # fallback

    file_urls = []
    
    # Process uploaded files (image/audio/video/pdf/etc.)
    if files:
        for file in files:
            # Skip string inputs or empty values (Swagger may send "")
            if isinstance(file, str) or not file:
                continue
            try:
                if file and file.filename:
                    file_bytes = await file.read()
                    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or ""

                    # Detect extension
                    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
                    if not ext and content_type:
                        ext = mimetypes.guess_extension(content_type) or 'bin'
                        ext = ext.lstrip('.')

                    # Determine folder by type
                    if "image" in content_type:
                        folder = "images"
                    elif "audio" in content_type:
                        folder = "audios"
                    elif "video" in content_type:
                        folder = "videos"
                    elif "pdf" in content_type or file.filename.lower().endswith(".pdf"):
                        folder = "pdfs"
                    else:
                        folder = "misc"

                    object_key = f"{folder}/{uuid.uuid4()}.{ext}"
                    url = upload_to_r2(file_bytes, object_key)
                    file_urls.append(url)
            except Exception as e:
                print(f"File upload failed: {str(e)}")

    prompt= correct_spelling(prompt)
    platform, full_prompt= get_history(chat_id, prompt)     

    t_manager = TokenManager(auth_token, prompt, model)
    if t_manager.is_enough_token(): 
            result = run_multi_agent_chain(user_id,chat_id, platform, model, prompt, full_prompt,youtube_url, file_urls)

            print("used_cost------------", result['response']['price'])
            if result['response']['price']:
                res = update_user_token(user_id, auth_token, result['response']['price'])
                print(res)
            return result    
 
    else:
        return "Insufficient Token! Please upgrade your plan"
    