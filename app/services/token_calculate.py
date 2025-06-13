import tiktoken

def count_tokens(text:str, model):
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        # Fallback for unsupported models
        return len(text.split())  # rough word-level token count

def price_calculate(platform: str, prompt: str, response: str):
    platform = platform.lower()

    if platform == 'chatgpt':
        model = 'gpt-4'
        input_price = 0.01 / 1000  # USD per token
        output_price = 0.03 / 1000
    elif platform == 'grok':
        model = 'llama3-70b-8192'
        input_price = 0.002 / 1000
        output_price = 0.002 / 1000
    elif platform == 'gemini':
        model = 'gemini-1.5-pro'
        input_price = 0.001 / 1000
        output_price = 0.002 / 1000
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    input_tokens = count_tokens(prompt, model)
    output_tokens = count_tokens(response, model)

    total_cost = input_tokens * input_price + output_tokens * output_price

    return {
        "platform": platform,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_cost_usd": round(total_cost, 6)
    }

result = price_calculate('chatgpt', "Tell me a joke", "Why did the chicken cross the road?")
print(result)

