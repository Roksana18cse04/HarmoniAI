import requests
def store_generated_message(userId, chatId, prompt, response, intend, runtime, input_urls=[], eachlabs_info=None, llm_model=None):
    print("response----------", response)
    inputs = [{"type": "text", "content": prompt}]
    responses=[]
    if intend=='caption-create':
        inputs.append({"type": "image", "content": input_urls})
    elif intend=='chat' or intend=='question-answering':
        responses.append({'type': 'text', 'content': response['output']})
    elif intend=='chat':
        responses.append({'type': 'text', 'content': response['result']})
    elif intend=='image-to-image':
        responses.append({'type': 'image', 'content': response['output']})
        responses.append({'type': 'image', 'content': response['output']})
    elif intend == 'voice-to-voice':
        inputs.append({"type": "audio", "content": input_urls})
        responses.append({'type': 'audio', 'content': response['output']})
    elif intend == 'voice-to-text':
        inputs.append({"type": "audio", "content": input_urls})
        responses.append({'type': 'audio', 'content': response['output']})
    elif intend == 'text-to-image':
        responses.append({'type': 'image', 'content': response['output']})
    elif intend == 'text-to-video':
        responses.append({'type': 'video', 'content': response['output']})
    elif intend == 'video-to-text':
        inputs.append({"type": "video", "content": input_urls})
        responses.append({'type': 'text', 'content': response['output']})
    elif intend == 'pdf-to-text':
        inputs.append({"type": "pdf", "content": input_urls})
        responses.append({'type': 'text', 'content': response['output']})
    elif intend=='shopping':
        responses.append({ 
            "type": "card",
            "isCard": True,
            "cardContent": [
                {
                    "id":response['output']['id'],
                    "title": response['output']['title'],
                    "description": response['output']['description'],
                    "type": "image",
                    "file": response['output']['link'],
                    "image": response['output']['image'],
                    "price": response['output']['price']
                }]   
            })
    print(f"----------------------------------------")
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
