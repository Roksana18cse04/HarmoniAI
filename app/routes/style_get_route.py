from fastapi import APIRouter, Query
from typing import List
from app.services.get_style_slug_name import get_style_slugs_by_model

router = APIRouter()

@router.get("/get-style-slugs")
def get_style_slugs(model_name: str = Query(..., description="Name of the model")) -> List[str]:
    return get_style_slugs_by_model(model_name)