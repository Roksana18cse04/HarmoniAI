import tiktoken

def count_tokens(text, model="gpt-4-0125-preview"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def price_calculate(platform, prompt, response):
    return 0
