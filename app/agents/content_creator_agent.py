from openai import OpenAI
from app.services.price_calculate import price_calculate
from app.services.llm_provider import LLMProvider
import json
import os
from dotenv import load_dotenv
load_dotenv()

client= OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_content_from_instruction(instruction,platform:str):
    system_prompt = """
You are a smart content creation assistant. A user will give you a free-form instruction describing what kind of content they want to post (e.g., "write a LinkedIn post about joining a new company", "write a tweet about AI", etc).

Your job is to:
- Understand the platform (LinkedIn, Instagram, blog, etc.)
- Generate high-quality, platform-appropriate content
- Use the correct tone (e.g., professional for LinkedIn, casual for Instagram)
- Include structure, hashtags, and emojis only if appropriate for the platform
- Assume the content is from a first-person point of view unless stated otherwise
- Behave like multilingual
""".strip()

    user_prompt = f"Instruction: {instruction}"
    
    llm = LLMProvider(platform)
    response = llm.generate_response(system_prompt, user_prompt)

    price = price_calculate(platform, instruction, response)
    return {
        "response": response,
        "price": price['price'],
        "input_token": price['input_token'],
        "output_token": price['output_token']
    }


