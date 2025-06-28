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

def price_calculate(platform: str, model, prompt: str, response: str):
    platform = platform.lower()

    # get pricing
    api_url = f"https://harmoniai-backend.onrender.com/api/v1/llm-model/get-all-llm-model?isDeleted=false&searchTerm={model}"
    res = requests.get(api_url)
    res.raise_for_status()
    data = res.json()

    results = data['data']['result']

    matched_model = next(
        (item for item in results if item.get('name') == model),
        None
    )

    if matched_model:
        input_price = matched_model.get('inputTokenPrice', 0)
        output_price = matched_model.get('outputTokenPrice', 0)
    else:
        print(f"[price_calculate] No matching model found for: {model}")
        input_price = output_price = 0
    
    input_price = input_price / 1000
    output_price = output_price / 1000
    
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
