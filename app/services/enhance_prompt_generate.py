from dotenv import load_dotenv
import os
from openai import OpenAI
import google.generativeai as genai

# Load environment variables
load_dotenv(override=True)

# Initialize API clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def enhance_prompt(base_prompt: str, target_model: str,platform:str) -> str:
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
    
    platform = platform.upper()

    try:
        if platform == "CHATGPT":
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a prompt enhancement expert."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            if response.choices and response.choices[0].message:
                enhanced = response.choices[0].message.content.strip()

        elif platform == "GEMINI":
            gemini_chat = genai.GenerativeModel("gemini-pro").start_chat()
            enhanced = gemini_chat.send_message(
                f"You are a prompt enhancement expert.\n{enhancement_prompt}"
            ).text.strip()

        elif platform == "GROK":
            raise NotImplementedError("GROK is not available via API yet. No enhancement supported.")

        else:
            raise ValueError(f"Unsupported platform: {platform}")

        # Clean output
        enhanced = enhanced.replace('\\', '').strip('"')
        return enhanced

    except Exception as e:
        print(f"[{platform}] Error enhancing prompt: {e}")
        return base_prompt
# Example usage
if __name__ == "__main__":
    base_prompt = "I want to produce a dog image"
    target_model = "DALL-E"  # Try with "DALL-E", "Midjourney", etc.
    
    enhanced = enhance_prompt(base_prompt, target_model)
    print(f"Base prompt: {base_prompt}")
    print(f"Enhanced for {target_model}: {enhanced}")