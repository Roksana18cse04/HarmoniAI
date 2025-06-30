from openai import OpenAI
from app.services.price_calculate import price_calculate
from app.services.llm_provider import LLMProvider
import base64
from typing import Optional
from app.config import config
from fastapi import UploadFile
import shutil
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_caption_from_instruction(platform, model, instruction: str, image_url):
    system_prompt = """
You are a smart caption creation assistant. A user will give you either:
- A free-form instruction describing what kind of content they want to post (e.g., "write a LinkedIn post")
- An image and instruction (e.g., "write an Instagram caption for this photo")

Your job is to:
- Analyze the image content if provided
- Understand the platform or tone implied by the instruction
- Generate a high-quality, engaging caption that aligns with the instruction (and image, if any)
- Include emojis, hashtags, and formatting only if appropriate for the platform
- Write in first person unless told otherwise
- Behave like multilingual
"""

    user_content = [{"type": "text", "text": instruction}]
    
    # if image_path:
    #     with open(image_path, "rb") as img_file:
    #         encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
    #     image_url = f"data:image/jpeg;base64,{encoded_image}"
    #     user_content.append({"type": "image_url", "image_url": {"url": image_url}})

    system_prompt= system_prompt.strip()
    user_prompt = user_content if image_url else instruction

    llm = LLMProvider(platform, model)
    response = llm.generate_response(system_prompt, user_prompt)
    price = price_calculate(platform,model, user_prompt, response['content'])
    return {
        "status": response['status'],
        "output": response['content'],
        "price": price['price'], 
        "input_token": price['input_token'],
        "output_token": price['output_token']
    }


# def caption_generator(platform, model, instruction, image_url):
#     image_path = None

#     if file:
#         image_path = os.path.join(config.IMAGE_PATH, file.filename)
#         os.makedirs(config.IMAGE_PATH, exist_ok=True)
#         with open(image_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#     try:
#         return generate_caption_from_instruction(platform, model, instruction, image_url)
#     finally:
#         if image_path and os.path.exists(image_path):
#             os.remove(image_path)
