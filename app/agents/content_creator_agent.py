from openai import OpenAI
import json
import os
from dotenv import load_dotenv
load_dotenv()

client= OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_content_from_instruction(instruction):
    system_prompt = """
You are a smart content creation assistant. A user will give you a free-form instruction describing what kind of content they want to post (e.g., "write a LinkedIn post about joining a new company", "write a tweet about AI", etc).

Your job is to:
- Understand the platform (LinkedIn, Instagram, blog, etc.)
- Generate high-quality, platform-appropriate content
- Use the correct tone (e.g., professional for LinkedIn, casual for Instagram)
- Include structure, hashtags, and emojis only if appropriate for the platform
- Assume the content is from a first-person point of view unless stated otherwise
"""

    user_prompt = f"Instruction: {instruction}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ],
        temperature=0.7,
        max_tokens=500
    )
    # print("response-------------", response)
    result_content = response.choices[0].message.content.strip()  # Access message content here
    return result_content


