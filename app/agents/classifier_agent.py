from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize OpenAI or use your preferred LLM provider
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_prompt_agent(prompt: str, categories_list: list) -> dict:
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
        {"prompt": "Rewrite this paragraph in simpler terms", "intent": "text-to-text"},
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

        {"prompt": "I want to watch a movie", "intent": "movie-recommendation"},
        {"prompt": "Show me popular comedies", "intent": "movie-recommendation"},
        {"prompt": "What's trending on Netflix?", "intent": "movie-recommendation"},
        {"prompt": "Suggest an action film for tonight", "intent": "movie-recommendation"},

        {"prompt": "What is the capital of France?", "intent": "question-answering"},
        {"prompt": "Who is the president of the USA?", "intent": "question-answering"},
        {"prompt": "What is the latest news in Bangladesh?", "intent": "question-answering"},
        {"prompt": "Tell me something about ChatGPT", "intent": "question-answering"},
        {"prompt": "What's the weather today in London?", "intent": "question-answering"}


    ]

    
    example_prompt = "\n".join([f"- {ex['prompt']} → {ex['intent']}" for ex in examples])

    # System prompt to classify user input and suggest tools based on the category ID
    system_prompt = (
        "You are an intent classification agent. Your task is to:\n"
        "1. Read the user's prompt and identify its high-level intent from the list of categories.\n"
        "2. If the user is asking a factual question, general knowledge, current events, or information (e.g., about AI, weather, history), classify it as 'question-answering'.\n"
        "3. If the user is asking to buy, compare, or browse products, classify as 'shopping'.\n"
        "4. If the user is asking about movies, TV shows, or streaming content, classify as 'movie-recommendation'.\n"
        "5. Otherwise, classify the intent based on common AI tasks such as image generation, text summarization, voice synthesis, or file conversion using the most relevant intent slug from the category list.\n"
        "\nHere are some example prompts and their intents:\n"
        f"{example_prompt}\n"
        f"\nCategories:\n{json.dumps(formatted_categories, indent=2)}\n"
        "\nRespond ONLY in this JSON format:\n"
        "{\n  \"intent\": \"slug\",\n  \"category_id\": number\n}"
    )




    # Send prompt to OpenAI
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    # Parse and return LLM response
    try:
        result_json = json.loads(response.choices[0].message.content.strip())
        print("prompt classifier result:------------------", result_json)
        return result_json
    except json.JSONDecodeError:
        return {
            "intent": None,
            "category_id": None,
            "error": "Failed to parse LLM response"
        }

