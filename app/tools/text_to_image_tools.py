# app/tools/image_tool.py

from app.schemas.TextToImage import TextToImageRequest
from app.agents.image_generator_agent import text_to_generate_image

async def handle_text_to_image(data: dict) -> str:
    request = TextToImageRequest(**data)
    result = text_to_generate_image(request)
    print(f" Result: {result}")
    return result["image_url"]
