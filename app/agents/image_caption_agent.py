from openai import OpenAI
from app.services.price_calculate import count_tokens
import base64
from typing import Optional
from app.config import config
from fastapi import UploadFile
import shutil
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_caption_from_instruction(instruction: str, image_path: Optional[str] = None):
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
    
    if image_path:
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
        image_url = f"data:image/jpeg;base64,{encoded_image}"
        user_content.append({"type": "image_url", "image_url": {"url": image_url}})

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_content if image_path else instruction}
        ],
        max_tokens=500,
        temperature=0.7
    )

    result_content = response.choices[0].message.content.strip()
    input_token = count_tokens(instruction)
    output_token = count_tokens(result_content)
    
    return {
        "response": result_content,
        "input_token": input_token,
        "output_token": output_token
    }


def caption_generator(file: UploadFile, instruction):
    image_path = None

    if file:
        image_path = os.path.join(config.IMAGE_PATH, file.filename)
        os.makedirs(config.IMAGE_PATH, exist_ok=True)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    try:
        return generate_caption_from_instruction(instruction, image_path)
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
