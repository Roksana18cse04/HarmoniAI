from app.services.fetch_models_info import fetch_models_info
from app.agents.classifier_agent import classify_prompt_agent
from app.agents.shopping_agent import shopping_agent    


def run_multi_agent_chain(prompt):
    # fetch all models info from eachlabs
    models_info=fetch_models_info()

    # load all categories from models info
    categories_list = models_info["result"]["result"]["categories"]
    print("categories list:------------------", categories_list)

    # classify the prompt using the models categories
    model_category = classify_prompt_agent(prompt, categories_list)
    print("model_category:------------------", model_category)
    print("model_category['intend']:------------------", model_category["intend"])
    if model_category["intend"]=="unknown":
        return "Sorry, I can't help with that."
    elif model_category["intend"]=="shopping":
        # if the category is shopping, use the shopping agent to get product info
        shopping_result = shopping_agent(prompt)
        return shopping_result
    else:
        # fetch models based on the classified category
        models_list = models_info["result"]["result"]["models"]
        category_id = model_category["category_id"] 
        if category_id is not None:
            models = [{
                "prompt": prompt,
                "title": model["title"], 
                'name': model["slug"],
                "thumbnail_url": model["thumbnail_url"],
                "price": model["gpu_device_id"]["price"],
            } for model in models_list if model["category"]["id"] == category_id]
        else:
            models = []
        print("models:------------------", models)      
        

        return models
