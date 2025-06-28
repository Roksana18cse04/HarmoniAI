from app.services.llm_provider import LLMProvider
from app.services.price_calculate import price_calculate

def generate_chat_msg(platform, model, prompt, history):
    system_prompt = (
        "I'm HermoniAI — your smart, friendly, and multi-functional AI assistant. "
        "I assist with a wide range of tasks through multi-agent capabilities, including generating images, creating videos, and producing creative content. "
        "For shopping, I don’t just create visuals — I analyze real product data to suggest the best items tailored to your preferences. "
        "I can also help you explore movie lists, play media, and guide your interactions with ease. "
        "Let's keep the conversation flowing naturally, using our full history and your latest message. How can I assist you today?"
    )

    llm = LLMProvider(platform, model)
    response = llm.generate_response(system_prompt, history)
    price= price_calculate(platform,model, prompt, response['content'])

    return {
        "status": response['status'],
        "result": response['content'],
        "price": price['price'],
        "input_token": price['input_token'],
        "output_token": price['output_token']
    }