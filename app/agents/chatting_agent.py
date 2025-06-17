from app.services.llm_provider import LLMProvider

def generate_chat_msg(platform, prompt, history):
    system_prompt = (
        "You are a friendly and helpful AI assistant. Continue the conversation naturally, "
        "based on the full history and the latest user message."
    )
    llm = LLMProvider(platform)
    response = llm.generate_response(system_prompt, prompt)
    return response