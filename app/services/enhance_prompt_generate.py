from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables from a .env file
load_dotenv()

# Get the OpenAI API key from the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client with the API key
client = OpenAI(api_key=OPENAI_API_KEY)

def enhance_prompt(base_prompt: str, target_model: str) -> str:
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
        # Create a chat completion
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a prompt enhancement expert."},
                {"role": "user", "content": enhancement_prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Extract the enhanced prompt from the response
        if response.choices and response.choices[0].message:
            enhanced_prompt = response.choices[0].message.content.strip()
            # Correctly replace newline characters and escaped quotes
            enhanced_prompt = enhanced_prompt.replace('\\', '')
            # Optionally remove surrounding quotes if desired
            enhanced_prompt = enhanced_prompt.strip('"')

            return enhanced_prompt
        return base_prompt  # fallback if no response
    
    except Exception as e:
        print(f"Error enhancing prompt: {e}")
        return base_prompt

# Example usage
if __name__ == "__main__":
    base_prompt = "I want to produce a dog image"
    target_model = "DALL-E"  # Try with "DALL-E", "Midjourney", etc.
    
    enhanced = enhance_prompt(base_prompt, target_model)
    print(f"Base prompt: {base_prompt}")
    print(f"Enhanced for {target_model}: {enhanced}")