from app.services.fetch_models_info import fetch_models_info
from app.agents.classifier_agent import classify_prompt_agent
from app.agents.image_caption_agent import caption_generator
from app.agents.shopping_agent import shopping_agent  
from app.agents.qa_agent import question_answer_agent 
from app.services.correct_symspell import correct_spelling
from typing import Optional
from fastapi import UploadFile

def fetch_models(prompt, models_info, model_category):
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

def run_multi_agent_chain(prompt, file:Optional[UploadFile] = None):
    # correct prompt spelling 
    prompt= correct_spelling(prompt)

    # fetch all models info from eachlabs
    models_info=fetch_models_info()

    # load all categories from models info
    categories_list = models_info["result"]["result"]["categories"]
    # Inject custom category
    categories_list.append({
        "id": 9999,  # Use a high unused ID to avoid collisions
        "name": "Question Answering",
        "slug": "question-answering",
        "count": 1
        
    })

    print("categories list:------------------", categories_list)

    # classify the prompt using the models categories
    model_category = classify_prompt_agent(prompt, categories_list)
    print("model_category:------------------", model_category)

    print("model_category['intent']:------------------", model_category["intent"])
    if model_category["intent"]=="unknown":
        return "Sorry, I can't help with that."
    elif model_category["intent"]=="shopping":
        # if the category is shopping, use the shopping agent to get product info
        shopping_result = shopping_agent(prompt)
        return shopping_result
    elif model_category["intent"]=="question-answering":
        response= question_answer_agent(prompt)
        print("result------", response)
        return {
            "result": response,
            "intent": "question-answering"
        }
    elif model_category['intent']=="caption-create":
        if file is None:
                return {
                    "error": "File is required for caption generation",
                    "intent": "caption-create"
                }
            
            # Additional file validation
        if not hasattr(file, 'filename') or not file.filename:
            return {
                "error": "Invalid file provided for caption generation",
                "intent": "caption-create"
            }
        caption_text= caption_generator(file, prompt)
        return caption_text
  
    else:
        # fetch models based on the classified category
        models= fetch_models(prompt, models_info, model_category)
        return models
