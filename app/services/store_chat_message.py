

import requests

def store_generated_message(userId, chatId, prompt, response, intend, runtime, input_urls=[], eachlabs_info=None, llm_model=None):
    inputs = [{"type": "text", "content": prompt}]
    responses=[]
    if intend=='caption-create':
        inputs.append({"type": "image", "content": input_urls})
    elif intend=='chat' or intend=='question-answering':
        responses.append({'type': 'text', 'content': response['output']})
    elif intend=='shopping' or intend=='media-recommendation':
        card_items = []

        for product in response['output']:
            # Extract numeric value from "799.00 TRY"
            try:
                price_str = product['price']
                numeric_price = float(price_str.split()[0])  # '799.00' from '799.00 TRY'
            except (ValueError, IndexError):
                numeric_price = 0.0  # fallback if format is invalid
            if intend=='shopping':
                card_items.append({"id": product['id']})
            elif intend=='media-recommendation':
                card_items.append({"id": None})
                
            card_items.append({
                "title": product['title'],
                "description": product['description'],
                "type": "image",
                "image": product['image'],
                "file": product['link'],
                "price": numeric_price
            })
        responses.append({
            "type": "card",
            "isCard": True,
            "cardContent": card_items
        })
        
        
    llm_model_info=None
    if llm_model:
        llm_model_info = {
            'name':llm_model,
            'status': response['status'],
            'input_token': response['input_token'],
            'output_token': response['output_token']
        }

    data = {
        "chatId": chatId,
        "userId": userId,
        "price": response['price'],
        "modelInfo": {
            'eachlabs_model': eachlabs_info,
            'llm_models': llm_model_info
        },
        "intend": intend,
        "runtime": runtime,
        "prompt": inputs,
        "response": responses
    }

    try:
        r = requests.post("https://harmoniai-backend.onrender.com/api/v1/conversations/add-message", json=data)
        print("Stored message:", r.json())
    except Exception as e:
        print("Failed to store message:", str(e))
