from app.services.fetch_models_info import fetch_models_info
from app.agents.classifier_agent import classify_prompt_agent
from app.agents.content_creator_agent import generate_content_from_instruction
from app.agents.image_caption_agent import generate_caption_from_instruction
from app.agents.shopping_agent import shopping_agent  
from app.agents.media_agent import media_agent
from app.agents.qa_agent import question_answer_agent 
from app.agents.chatting_agent import generate_chat_msg
from app.services.store_chat_message import store_generated_message
import mimetypes
import time


def is_image_url(url: str) -> bool:
    # Method 1: Check file extension (fallback)
    # image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff', '.heic')
    # if any(url.lower().endswith(ext) for ext in image_extensions):
    #     return True

    # Optional: Method 2 - HEAD request to detect Content-Type (requires requests lib)
    # Slower but more accurate
    try:
        import requests
        response = requests.head(url, timeout=2)
        content_type = response.headers.get("Content-Type", "")
        return content_type.startswith("image/")
    except Exception:
        return False

def fetch_models(models_info, model_category):
    models_list = models_info["result"]["result"]["models"]
    print(model_category)
    category_id = model_category["id"] 
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

def run_multi_agent_chain( user_id, chat_id, platform, model, prompt, full_prompt, youtube_url, file_urls):

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
    intent = model_category['content']["intent"]
    print("model_category['intent']:------------------", intent)

    if intent=="unknown":
        return {
            "user_prompt": prompt,
            "response": "Sorry, I can't help with that.",
            "model_info": {
                'llm_model_name': model
            },
            "intend": "unknown",
            "runtime": round( time.time()-start_time, 3)
        }
    elif intent=="shopping":
        # if the category is shopping, use the shopping agent to get product info
        response = shopping_agent(platform, model, prompt)
        runtime = round(time.time() - start_time, 3)
        print("response------------", response)
        # call a route to store message on database
        store_generated_message(
            userId=user_id, 
            chatId=chat_id, 
            prompt=prompt, 
            response=response, 
            intend=intent, 
            runtime=runtime,
            llm_model=model  
        )

        return {
            "prompt": prompt,
            "response": response,
            "model_info": {
                'llm_model': {
                    'name': model
                }
            },
            "intend": "shopping",
            "runtime": runtime
        }
    elif intent=="media-recommendation":
        response = media_agent(platform, model, prompt) 
        runtime = round(time.time() - start_time, 3)
        # call a route to store message on database
        store_generated_message(
            userId=user_id, 
            chatId=chat_id, 
            prompt=prompt, 
            response=response, 
            intend=intent, 
            runtime=runtime,
            llm_model=model  
        )
        return {
            "prompt": prompt,
            "response": response,
            "model_info": {
                'llm_model':{
                    'name':model,
                }
            },
            "intend": "media-recommendation",
            "runtime": runtime
        }     
    elif intent=="question-answering":
        start_time = time.time()
        response= question_answer_agent(platform, model, prompt, full_prompt)
        print("result------", response)
        runtime = round(time.time() - start_time, 3)
        # call a route to store message on database
        store_generated_message(
            userId=user_id, 
            chatId=chat_id, 
            prompt=prompt, 
            response=response, 
            intend=intent, 
            runtime=runtime,
            llm_model=model  
        )
        return {
            "user_prompt": prompt,
            "response": response,
            "model_info": {
                'llm_models':{
                    'name': model
                }
            },
            "intend": "question-answering",
            "runtime": round( time.time()-start_time, 3)
        }
    elif intent=="caption-create":

        # Step 1: Filter only image URLs
        image_urls = [
            url for url in file_urls
            if is_image_url(url)
        ]
        print("image_urls-------------", image_urls)
        # Step 2: Use the first image only for captioning
        try:
            if image_urls:
                image_url=image_urls[0]
            else: image_url= None

            response = generate_caption_from_instruction(platform, model, prompt, image_url)
            runtime = round(time.time() - start_time, 3)
            # call a route to store message on database
            store_generated_message(
                userId=user_id, 
                chatId=chat_id, 
                prompt=prompt, 
                response=response, 
                intend=intent, 
                runtime=runtime,
                input_urls=image_url,
                llm_model=model  
            )
        except Exception as e:
                raise Exception(f"Caption generation failed: {str(e)}")

        return {
            "user_prompt": prompt,
            "response": response,
            "model_info": {
                'llm_models':{
                    'name': model
                }
            },
            "intend": "caption-create",
            "runtime": runtime,
            "input_image_url": image_urls[0] if image_urls else None
        }

    
    elif intent == 'content-create':
        response = generate_content_from_instruction(platform, model, prompt)

        # for image and vedio generation , send eachlabs models list
        if 'image' in response['media_type']:
            category = next((category for category in categories_list if category.get('slug') == 'text-to-image'), None)
            models = fetch_models(models_info, category)
        elif 'vedio' in response['media_type']:
            category = next((category for category in categories_list if category.get('slug') == 'text-to-vedio'), None)
            models = fetch_models(models_info, category)
        else:
            models=[]
        runtime = round( time.time()-start_time, 3)
        # call a route to store message on database
        store_generated_message(
            userId=user_id, 
            chatId=chat_id, 
            prompt=prompt, 
            response=response['data'], 
            intend=intent, 
            runtime=runtime,
            llm_model=model  
        )

        return {
            "user_prompt": prompt,
            "response": response['data'],
            "model_info": {
                'eachlabs_models': {
                    'model_list': models
                },
                'llm_models': {
                    'name': model,
                }
                
            },
            "intend": "content-generate",
            "runtime": round( time.time()-start_time, 3)
        }
    elif intent == 'chat':
        response = generate_chat_msg(platform, model, prompt, full_prompt)
        runtime = round( time.time()-start_time, 3)
        # call a route to store message on database
        store_generated_message(
            userId=user_id, 
            chatId=chat_id, 
            prompt=prompt, 
            response=response, 
            intend=intent, 
            runtime=runtime,
            llm_model=model  
        )

        return {
            "user_prompt": prompt,
            "response": response['output'],
            "price": response['price'],
            "model_info": {
                'llm_models': {
                    'name': model,
                    'status': response['status'],
                    'input_token': response['input_token'],
                    'output_token': response['output_token']
                }
            },
            "intend": "chat",
            "runtime": runtime
        }
    else:
        # fetch models based on the classified category
        models= fetch_models(models_info, model_category)
        if not models:
            return {
                "user_prompt": prompt,
                "eachlabs_models": [],
                "message": "Currently, model is not available",
                # "runtime": round( time.time()-start_time, 3)
            }
        return {
            "user_prompt": prompt,
            "eachlabs_models": models,
            "intend": intent,
            # "runtime": round( time.time()-start_time, 3)
        }
