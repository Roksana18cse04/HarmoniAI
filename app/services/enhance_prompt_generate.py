from dotenv import load_dotenv
import os
from app.services.llm_provider import LLMProvider
from app.services.token_calculate import price_calculate

load_dotenv(override=True)

def enhance_prompt(base_prompt: str, target_model: str, platform: str) -> tuple[str, str]:
    """
    Enhances the base prompt specifically tailored for the target_model using the chosen platform.
    Returns a tuple of (price, enhanced_prompt).
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
        enhanced = llm.generate_response(system_prompt="", user_prompt=enhancement_prompt)
        
        # Clean output if necessary
        enhanced = enhanced.replace('\\', '').strip('"').strip()
        
        # Calculate price based on base prompt and enhanced prompt
        price = price_calculate(base_prompt, enhanced)
        
        return price, enhanced
    
    except Exception as e:
        print(f"[{platform}] Error enhancing prompt: {e}")
        return 0.0, base_prompt
