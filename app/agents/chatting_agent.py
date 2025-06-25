from app.services.llm_provider import LLMProvider
from app.services.price_calculate import price_calculate

def generate_chat_msg(platform, prompt, history):
    system_prompt = (
        "You are a friendly and helpful AI assistant. Continue the conversation naturally, "
        "based on the full history and the latest user message."
    )
    llm = LLMProvider(platform)
    response = llm.generate_response(system_prompt, prompt)
    price= price_calculate(platform, prompt, response['content'])

    return {
        "status": response['status'],
        "result": response['content'],
        "price": price['price'],
        "input_token": price['input_token'],
        "output_token": price['output_token']
    }