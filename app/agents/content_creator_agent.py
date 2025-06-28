from openai import OpenAI
from app.services.price_calculate import price_calculate
from app.agents.image_generator_agent import text_to_generate_image
from app.agents.vedio_generator_agent import text_to_video_generate
from app.services.llm_provider import LLMProvider
import json
import os
from dotenv import load_dotenv
load_dotenv()

client= OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_instruction_with_llm(platform, model, instruction):
    media_director_prompt = """
You're a content media director AI. Given a user's instruction, classify which content type(s) should be generated: "text", "image", "video", or any combination.
Output JSON in the format:
{
  "media_types": ["text", "image"]
}
"""
    llm = LLMProvider(platform, model)

    user_prompt = f"Instruction: {instruction}"
    response = llm.generate_response(media_director_prompt, user_prompt)
    return json.loads(response['content'])

def generate_content_from_instruction(platform, model, instruction):

    system_prompt = """
You are a smart content creation. A user will give you a free-form instruction describing what kind of content they want to post (e.g., "write a LinkedIn post about joining a new company", "write a tweet about AI", etc).

Your job is to:
- Understand the platform (LinkedIn, Instagram, blog, etc.)
- Generate high-quality, platform-appropriate content
- Use the correct tone (e.g., professional for LinkedIn, casual for Instagram)
- Include structure, hashtags, and emojis only if appropriate for the platform
- Assume the content is from a first-person point of view unless stated otherwise
- Behave like multilingual
""".strip()

    user_prompt = f"Instruction: {instruction}"
    
    llm = LLMProvider(platform, model)
    text_response = llm.generate_response(system_prompt, user_prompt)

    analysis = analyze_instruction_with_llm(platform, model, instruction)

    price = price_calculate(platform, model, instruction, text_response['content'])
    return {
        "media_type": analysis['media_types'],
        "result":{
            "response": text_response,
            "price": price['price'],
            "input_token": price['input_token'],
            "output_token": price['output_token']
        }
    }


