from app.services.fetch_models_info import fetch_models_info
from app.agents.classifier_agent import classify_prompt_agent
from app.agents.image_caption_agent import caption_generator
from app.agents.content_creator_agent import generate_content_from_instruction
from app.agents.shopping_agent import shopping_agent  
from app.agents.media_agent import media_agent
from app.agents.qa_agent import question_answer_agent 
from app.agents.chatting_agent import generate_chat_msg
from typing import Optional
from fastapi import UploadFile
import time

def fetch_models(models_info, model_category):
    models_list = models_info["result"]["result"]["models"]
    category_id = model_category["category_id"] 
    if category_id is not None:
        models = [{
            "title": model["title"], 
            'name': model["slug"],
            "thumbnail_url": model["thumbnail_url"],
            "price": model["gpu_device_id"]["price"],
            "intend":model["category"]["slug"]
        } for model in models_list if model["category"]["id"] == category_id]
    else:
        models = []
    print("models:------------------", models)      
    return models

def run_multi_agent_chain( platform, model, prompt, full_prompt, file:Optional[UploadFile] = None):
    start_time = time.time()
    print("platform---------------", platform)
    # correct prompt spelling 

    # fetch all models info from eachlabs
    models_info=fetch_models_info()

    # load all categories from models info
    categories_list = models_info["result"]["result"]["categories"]
    # Inject custom category
    categories_list.extend([{
        "id": 9999,  # Use a high unused ID to avoid collisions
        "name": "Question Answering",
        "slug": "question-answering",
        "count": 1
        
    },
    {
        'id': 10001,
        'name': 'Caption Create',
        'slug': 'caption-create',
        'count': 1
    },
    {
       'id': 10002,
        'name': 'Content Create',
        'slug': 'content-create',
        'count': 1 
    },
    {
        'id': 10003,
        'name': 'Shopping',
        'slug': 'shopping',
        'count': 1
    },
    {
        'id': 10004,
        'name': 'Media Recommendation',
        'slug': 'media-recommendation',
        'count': 1
    },
    {
        'id': 10005,
        'name': 'Chat',
        'slug': 'chat',
        'count': 1
    },
    {
        'id': 10006,
        'name': 'Unknown',
        'slug': 'unknown',
        'count': 1
    }
    ])

    # print("categories list:------------------", categories_list)

    # classify the prompt using the models categories
    model_category = classify_prompt_agent(platform, model, prompt, categories_list)
    print("model_category:------------------", model_category)

    print("model_category['intent']:------------------", model_category["intent"])
    if model_category["intent"]=="unknown":
        return {
            "user_prompt": prompt,
            "response": "Sorry, I can't help with that.",
            "model_info": {
                'model_name': model
            },
            "intend": "unknown",
            "runtime": round( time.time()-start_time, 3)
        }
    elif model_category["intent"]=="shopping":
        # if the category is shopping, use the shopping agent to get product info
        shopping_result = shopping_agent(platform, model, prompt)
        return {
            "user_prompt": prompt,
            "response": shopping_result,
            "model_info": {
                'model_name': model,
            },
            "intend": "shopping",
            "runtime": round( time.time()-start_time, 3)
        }
    elif model_category["intent"]=="media-recommendation":
        response = media_agent(platform, model, prompt) 
        return {
            "user_prompt": prompt,
            "response": response,
            "model_info": {
                'model_name': model
            },
            "intend": "media-recommendation",
            "runtime": round( time.time()-start_time, 3)
        }     
    elif model_category["intent"]=="question-answering":
        response= question_answer_agent(platform, model, prompt, full_prompt)
        print("result------", response)
        return {
            "user_prompt": prompt,
            "response": response,
            "model_info": {
                'model_name': model
            },
            "intend": "question-answering",
            "runtime": round( time.time()-start_time, 3)
        }
    elif model_category['intent']=="caption-create":
        # Use the file if provided and valid, otherwise pass None
        if file is not None and (not hasattr(file, 'filename') or not file.filename):
            file = None
        # Run caption generation (prompt-only or image+prompt)
        caption_text = caption_generator(platform, model, file, prompt)   
        return {
            "user_prompt": prompt,
            "response": caption_text,
            "model_info": {
                'model_name': model
            },
            "intend": "caption-create",
            "runtime": round( time.time()-start_time, 3)
        }  
    elif model_category['intent'] == 'content-create':
        response = generate_content_from_instruction(platform, model, prompt)

        # for image and vedio generation , send eachlabs models list
        if response['media_type'] == 'image':
            category = next((category for category in categories_list if category.get('slug') == 'text-to-image'), None)
            models = fetch_models(models_info, category)
        elif response['media_type'] == 'vedio':
            category = next((category for category in categories_list if category.get('slug') == 'text-to-vedio'), None)
            models = fetch_models(models_info, category)
        else:
            models=[]
        
        return {
            "user_prompt": prompt,
            "response": response['result'],
            "model_info": {
                'model_name': model,
                'eachlabs_models': models
            },
            "intend": "content-generate",
            "runtime": round( time.time()-start_time, 3)
        }
    elif model_category['intent'] == 'chat':
        response = generate_chat_msg(platform, model, prompt, full_prompt)
        return {
            "user_prompt": prompt,
            "response": response,
            "model_info": {
                'model_name': model
            },
            "intend": "chatting",
            "runtime": round( time.time()-start_time, 3)
        }
    else:
        # fetch models based on the classified category
        models= fetch_models(models_info, model_category)
        if not models:
            return {
                "user_prompt": prompt,
                "models": [],
                "message": "Currently, model is not available",
                # "runtime": round( time.time()-start_time, 3)
            }
        return {
            "user_prompt": prompt,
            "models": models,
            "intend": model_category['intent'],
            # "runtime": round( time.time()-start_time, 3)
        }
