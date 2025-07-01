from dotenv import load_dotenv
import os
from app.services.llm_provider import LLMProvider
from app.services.price_calculate import price_calculate

load_dotenv(override=True)

async def enhance_prompt(platform,base_prompt, eachlabs_model, llm_model, intend: str):
    """
    Enhances the base prompt specifically tailored for the target_model using the chosen platform.
    Returns an EnhanceResponse containing enhanced prompt and price.
    """
    enhancement_prompt = f"""
    Take the following base prompt and enhance it specifically for the {eachlabs_model} model.
    The enhanced version should incorporate appropriate improvements for better results.
    The task may involve one of the following:
    - Video generation
    - Image generation
    - Content creation (e.g., text, articles, or stories)
    - Audio or music creation
    - Code generation

    Base prompt: "{base_prompt}"

    Please respond with ONLY the enhanced prompt, no additional commentary or explanation.
    """
    try:
        llm = LLMProvider(platform, llm_model)
        response = llm.generate_response(system_prompt="", user_prompt=enhancement_prompt)
        enhance_prompt = response['content']
        enhanced = enhance_prompt.replace('\\', '').strip('"').strip()

        price = price_calculate(platform, llm_model, base_prompt, enhance_prompt)
        print(f"Enhanced prompt: {enhanced}")
        print(f" Price: {price}")
        
        return enhanced,price
            
    
    except Exception as e:
        print(f"[{platform}] Error enhancing prompt: {e}")
        
     