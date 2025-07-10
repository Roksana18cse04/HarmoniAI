from openai import OpenAI
from app.services.llm_provider import LLMProvider
import os
from dotenv import load_dotenv
import json
import re

load_dotenv(override=True)

# Initialize OpenAI or use your preferred LLM provider
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_prompt_agent(platform, model, prompt: str, categories_list: list) -> dict:
    # Prepare categories list in the format needed for the system prompt
    formatted_categories = [
        {
            "name": category["name"],
            "slug": category["slug"],
            "id": category["id"],
            "desc": f"Description: {category['name']} category"
        }
        for category in categories_list
    ]
    # Add example prompts to help GPT understand intent
    examples = [

        {"prompt": "a fantasy castle on a mountain", "intent": "text-to-image"},
        {"prompt": "photo of a cat", "intent": "text-to-image"},
        {"prompt": "sunset over the ocean", "intent": "text-to-image"},
        {"prompt": "a cartoon dog with sunglasses", "intent": "text-to-image"},
        {"prompt": "Generate a 3D model of a chair from a text prompt", "intent": "text-to-3d"},
        {"prompt": "Convert this PDF manual into editable text", "intent": "pdf-to-text"},
        {"prompt": "Describe the contents of this image", "intent": "image-to-text"},
        {"prompt": "Turn this sketch into a realistic image", "intent": "image-to-image"},
        {"prompt": "Animate this image into a short video", "intent": "image-to-video"},
        {"prompt": "Create a landscape from a text description", "intent": "text-to-image"},
        {"prompt": "Turn this script into spoken dialogue", "intent": "text-to-voice"},
        {"prompt": "Make a video from a story prompt", "intent": "text-to-video"},
        {"prompt": "Summarize the content of this video", "intent": "video-to-text"},
        {"prompt": "Convert this video into a stylized animation", "intent": "video-to-video"},
        {"prompt": "Transcribe this audio file into text", "intent": "voice-to-text"},
        {"prompt": "Translate this voice message to another language in the same voice", "intent": "voice-to-voice"},
        {"prompt": "Train a custom AI model with this dataset", "intent": "training"},
        {"prompt": "Connect two services using this API", "intent": "integration"},
        {"prompt": "Use this tool to resize an image", "intent": "utilities"},
        {"prompt": "Convert this photo into a 3D mesh", "intent": "image-to-3d"},

        {"prompt": "I want to buy a phone", "intent": "shopping"},
        {"prompt": "Show me some laptops under $1000", "intent": "shopping"},
        {"prompt": "Is there a discount on shoes?", "intent": "shopping"},
        {"prompt": "What’s the price of this item?", "intent": "shopping"},

        {"prompt": "Show me some trending movies", "intent": "media-recommendation"},
        {"prompt": "What are the top-rated series right now?", "intent": "media-recommendation"},
        {"prompt": "Play some relaxing music", "intent": "media-recommendation"},
        {"prompt": "Recommend me a good mystery book", "intent": "media-recommendation"},
        
        {"prompt": "Find a movie similar to Inception", "intent": "media-recommendation"},
        {"prompt": "Any new episodes released this week?", "intent": "media-recommendation"},
        {"prompt": "What songs are popular today?", "intent": "media-recommendation"},
        {"prompt": "Suggest a bestselling novel", "intent": "media-recommendation"},
        
        {"prompt": "I want to watch a comedy film", "intent": "media-recommendation"},
        {"prompt": "Show me Netflix originals", "intent": "media-recommendation"},
        {"prompt": "Play the latest Taylor Swift album", "intent": "media-recommendation"},
        {"prompt": "Is there a new Harry Potter book?", "intent": "media-recommendation"},

        {"prompt": "What is the capital of France?", "intent": "question-answering"},
        {"prompt": "Who is the president of the USA?", "intent": "question-answering"},
        {"prompt": "What is the latest news in Bangladesh?", "intent": "question-answering"},
        {"prompt": "Tell me something about ChatGPT", "intent": "question-answering"},
        {"prompt": "What's the weather today in London?", "intent": "question-answering"},

        {"prompt": "Write a blog post about the benefits of meditation", "intent": "content-create"},
        {"prompt": "Generate a product description for a new smartphone", "intent": "content-create"},
        {"prompt": "Create an Instagram post caption and content for a travel brand", "intent": "content-create"},
        {"prompt": "Write LinkedIn content for a marketing manager announcing a promotion", "intent": "content-create"},
        {"prompt": "Draft a newsletter for our spring sale campaign", "intent": "content-create"},

        # Caption creation
        {"prompt": "Create a caption for a dog wearing sunglasses", "intent": "caption-create"},
        {"prompt": "Write a short and witty caption for a coffee photo", "intent": "caption-create"},
        {"prompt": "Caption this birthday celebration image", "intent": "caption-create"},
        {"prompt": "Suggest a funny caption for a cat video", "intent": "caption-create"},
        {"prompt": "Give me a caption for a fitness transformation post", "intent": "caption-create"},

        # ----------- NEW: Chat / Conversational Intent -----------
        {"prompt": "hello, how are you?", "intent": "chat"},
        {"prompt": "What’s up?", "intent": "chat"},
        {"prompt": "Can you tell me a joke?", "intent": "chat"},
        {"prompt": "How’s the weather today?", "intent": "chat"},
        {"prompt": "What do you think about AI?", "intent": "chat"},
        {"prompt": "Tell me something interesting.", "intent": "chat"},
        {"prompt": "Can we chat for a bit?", "intent": "chat"},
        {"prompt": "I’m feeling bored, chat with me.", "intent": "chat"},
        {"prompt": "Do you like music?", "intent": "chat"},
        {"prompt": "How was your day?", "intent": "chat"},



    ]

    
    example_prompt = "\n".join([f"- {ex['prompt']} → {ex['intent']}" for ex in examples])

    # System prompt to classify user input and suggest tools based on the category ID
    system_prompt = (
        "You are a multilingual intent classification agent. Your task is to:\n"
        "1. Read the user's prompt and identify its high-level intent from the list of categories.\n"
        "2. If the user is asking a factual question, general knowledge, current events, or information (e.g., about AI, weather, history), classify it as 'question-answering'.\n"
        "3. If the user is asking to buy, compare, or browse products, classify as 'shopping'.\n"
        "4. If the user is asking about movies, TV shows, Series, Musics, Books,  or streaming content, classify as 'media-recommendation'.\n"
        "5. Otherwise, classify the intent based on common AI tasks such as image generation, text summarization, voice synthesis, or file conversion using the most relevant intent slug from the category list.\n"
        "\nHere are some example prompts and their intents:\n"
        f"{example_prompt}\n"
        f"\nCategories:\n{json.dumps(formatted_categories, indent=2)}\n"
        "⚠️ Do NOT use generic labels like 'text-to-text', 'text-generation', 'creative writing', or similar.\n"
        "Use only one of the intent slugs shown in the examples.\n"
        "Always return this exact JSON format:\n"
        "{\n  \"intent\": \"slug\",\n  \"category_id\": number\n}"
        "You support multilingual prompts (e.g., English, Turkish, Spanish, French, Arabic, etc.)."
    )
    
    llm = LLMProvider(platform, model)
    
    try:
        response = llm.generate_response(system_prompt, prompt)
        print("classifier agent response-------------", response['content'])
        return response
    
    except json.JSONDecodeError:
        return {
            "intend": None,
            "category_id": None,
            "error": "Failed to parse LLM response"
        }

