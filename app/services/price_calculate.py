import tiktoken
import requests
import json

def count_tokens(text: str, model):
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        return len(text.split())  # fallback
    except TypeError:
        raise ValueError(f"Invalid input to tokenizer: {text} (type {type(text)})")

def price_calculate(platform: str, prompt: str, response: str):
    platform = platform.lower()

    # get pricing
    api_url = "https://harmoniai-backend.onrender.com/api/v1/configure/get-configure"
    res = requests.get(api_url)
    res.raise_for_status()
    data = res.json()

    inputPrice = data['data']['models'][platform]['inputToken']
    outputPrice = data['data']['models'][platform]['outputToken']
    input_price = inputPrice / 1000
    output_price = outputPrice / 1000

    if platform == 'chatgpt':
        model = 'gpt-4'
    elif platform == 'grok':
        model = 'llama3-70b-8192'
    elif platform == 'gemini':
        model = 'gemini-1.5-pro'
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    
    if not isinstance(response, str):
        response = json.dumps(response)
        
    input_tokens = count_tokens(prompt, model)
    output_tokens = count_tokens(response, model)

    total_cost = input_tokens * input_price + output_tokens * output_price
    return {
        "price": round(total_cost, 6),
        "input_token": input_tokens,
        "output_token": output_tokens
    }
