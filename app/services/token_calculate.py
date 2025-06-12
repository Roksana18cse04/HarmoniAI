import tiktoken

def count_tokens(text, model):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def price_calculate(platform:str, prompt, response):
    platform = platform.lower()

    if platform=='chatgpt':
        model='gpt-4-0125-preview'
    elif platform == 'grok':
        model = 'llama3-70b-8192'
    elif platform == 'gemini':
        model = 'gemini-1.5-pro'
    input_token = count_tokens(prompt, model)
    output_token = count_tokens(response, model)

    # calculate price
    # for price per token hit backend api
    return 0
