from app.services.fetch_models_info import fetch_models_info
from app.agents.classifier_agent import classify_prompt_agent


def run_multi_agent_chain(prompt):
    # fetch all models info from eachlabs
    models_info=fetch_models_info()

    # load all categories from models info
    categories_list = models_info["result"]["result"]["categories"]
    print("categories list:------------------", categories_list)

    # classify the prompt using the models categories
    model_category = classify_prompt_agent(prompt, categories_list)
    print("model_category:------------------", model_category)

    # fetch models based on the classified category
    models_list = models_info["result"]["result"]["models"]
    category_id = model_category["category_id"]
    if category_id is not None:
        models = [{
            "title": model["title"], 
            'name': model["slug"],
            "thumbnail_url": model["thumbnail_url"],
            "price": model["gpu_device_id"]["price"],
        } for model in models_list if model["category"]["id"] == category_id]
    else:
        models = []
    print("models:------------------", models)      
    

    return models
