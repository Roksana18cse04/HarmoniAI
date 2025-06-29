

import requests

def store_generated_message(userId, chatId, prompt, response, intend, runtime, input_urls=[], eachlabs_info=None, llm_model=None):
    print("response----------", response)
    inputs = [{"type": "text", "content": prompt}]
    responses=[]
    if intend=='caption-create':
        inputs.append({"type": "image", "content": input_urls})
    elif intend=='chat':
        responses.append({'type': 'text', 'content': response['result']})

    data = {
        "chatId": chatId,
        "userId": userId,
        "price": response['price'],
        "modelInfo": {
            'eachlabs_model': eachlabs_info,
            'llm_models': {
                'name':llm_model,
                'status': response['status'],
                'input_token': response['input_token'],
                'output_token': response['output_token']
            }
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
