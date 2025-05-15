from openai import OpenAI
import base64
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_caption_from_image_and_instruction(image_path, instruction):
    system_prompt = """
You are a smart caption creation assistant. A user will give you an image and a free-form instruction describing what kind of content they want to post (e.g., "write a LinkedIn post about this photo", "create an Instagram caption", etc).

Your job is to:
- Analyze the image content
- Understand the platform or tone implied by the instruction (LinkedIn, Instagram, etc.)
- Generate a high-quality, engaging caption that aligns with the visual and instruction
- Include emojis, hashtags, and formatting only if appropriate for the platform
- Write in first person unless told otherwise
- Behave like multilingual
"""

    # Read and base64 encode the image
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        image_url = f"data:image/jpeg;base64,{encoded_image}"

    response = client.chat.completions.create(
        model="gpt-4-turbo",  # or "gpt-4-turbo" if it has vision access
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=500,
        temperature=0.7
    )

    result_content = response.choices[0].message.content.strip()
    print("result----------", result_content)
    return result_content

