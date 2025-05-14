import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()


# Your Eachlabs API key
API_KEY = os.getenv("EACHLABS_API_KEY")

# Function to get image caption from Eachlabs API
def get_image_caption(image_path):
    url = "https://api.eachlabs.ai/v1/image-captioning"  # Adjust URL based on Eachlabs' documentation
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    # Assuming the image is passed as base64 or URL
    with open(image_path, 'rb') as f:
        image_data = f.read()

    files = {
        'file': ('image.jpg', image_data, 'image/jpeg')
    }
    
    response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        caption = response.json()['caption']
        return caption
    else:
        raise Exception(f"Error in image captioning: {response.text}")

# Function to generate content based on caption using GPT model (or text generation model)
def generate_post(caption):
    url = "https://api.eachlabs.ai/v1/text-generation"  # Adjust URL for text generation API
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = json.dumps({
        "prompt": f"Create a social media post based on the following description: {caption}",
        "temperature": 0.7,
        "max_tokens": 150
    })
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        post_content = response.json()['text']
        return post_content
    else:
        raise Exception(f"Error in text generation: {response.text}")

# Example usage
image_path = r"app\data\road.jpg"
caption = get_image_caption(image_path)
generated_post = generate_post(caption)

print(generated_post)
