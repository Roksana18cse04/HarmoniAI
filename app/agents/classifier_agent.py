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
        {"prompt": "Generate a landscape from a text description", "intent": "text-to-image"},
        {"prompt": "photo of dog", "intent": "text-to-image"},
        {"prompt": "Change the style of an image to a painting", "intent": "image-to-image"},
        {"prompt": "Convert a PDF document to editable text", "intent": "pdf-to-text"}
    ]
    
    example_prompt = "\n".join([f"- {ex['prompt']} → {ex['intent']}" for ex in examples])

    # System prompt to classify user input and suggest tools based on the category ID
    system_prompt = (
        "You are a classification agent. Your job is to:\n"
        f"1. Classify the user's prompt into one of the following categories:\n{json.dumps(formatted_categories, indent=2)}\n"
        f"3. Here are some examples of prompts and their correct classifications:\n{example_prompt}\n"
        "Output strictly in this JSON format:\n"
        "{\n"
        "  \"intent\": \"slug\",\n"
        "  \"category_id\": number,\n"
        "}"
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
        return result_json
    except json.JSONDecodeError:
        return {
            "intent": None,
            "category_id": None,
            "error": "Failed to parse LLM response"
        }

