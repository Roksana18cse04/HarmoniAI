from dotenv import load_dotenv
import os
from app.services.llm_provider import LLMProvider
from app.services.price_calculate import price_calculate

load_dotenv(override=True)

async def enhance_prompt(base_prompt: str, target_model: str, platform: str, intend: str):
    """
    Enhances the base prompt specifically tailored for the target_model using the chosen platform.
    Returns an EnhanceResponse containing enhanced prompt and price.
    """
    enhancement_prompt = f"""
    Take the following base prompt and enhance it specifically for the {target_model} model.
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
        llm = LLMProvider(platform)
        enhanced_prompt = llm.generate_response(system_prompt="", user_prompt=enhancement_prompt)
        enhanced = enhanced_prompt.replace('\\', '').strip('"').strip()
        price = price_calculate(platform, base_prompt, enhanced)
        print(f"Enhanced prompt: {enhanced}")
        print(f" Price: {price}")
        
        return {
            "prompt": base_prompt,
            "enhanced_prompt": enhanced,
            "model_name": target_model,
            "price": price["price"],
            "input_token": price["input_token"],    # Fixed typo
            "output_token": price["output_token"],  # Fixed: was ["output_token"] (list)
            "intend": intend
        }
    
    except Exception as e:
        print(f"[{platform}] Error enhancing prompt: {e}")
        
        return {
            "prompt": base_prompt,
            "enhanced_prompt": base_prompt,  # Fixed: was using undefined 'enhanced' variable
            "model_name": target_model,
            "price": 0.0,
            "input_token": 0,    # Fixed typo
            "output_token": 0, 
            "intend": intend
        }