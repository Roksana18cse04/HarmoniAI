# services/category_loader.py
import json
from app.config import DATA_PATH 

def load_category_and_tools():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    categories = data["result"]["result"]["categories"]
    category_map = {cat["name"]: {"id": cat["id"], "slug": cat["slug"]} for cat in categories}
    print ("all categories:-------------", category_map)
    return category_map
