# routes.py
from fastapi import APIRouter, Form
from app.agents.chaining_agent import fetch_models
from app.services.fetch_models_info import fetch_models_info
router = APIRouter()

@router.get("/get-eachlabs-models-list/")
async def get_models_list():
    models_info =  fetch_models_info()
    models_list= models_info['result']['result']['models']
    models = [{
        "id": model["id"],
        "title": model["title"],
        "title_slug": model["slug"],
        "category_name": model['category']['name'],
        "category_name_slug": model["category"]["slug"],
        "image": model["thumbnail_url"],
        "price": model["gpu_device_id"]["price"]
    
    } for model in models_list]
    return {"models": models}
