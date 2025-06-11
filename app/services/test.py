import requests
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv(override=True)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
USE_GEMINI = os.getenv("USE_GEMINI", "False").lower() == "true"

# Setup clients
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if USE_GEMINI:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Eachlabs API Key
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Language database for model mapping
LANGUAGE_DATABASE = {
    "openvoice": {
        "english": "EN",
        "en": "EN",
        "es": "ES",
        "fr": "FR",
        "zh": "ZH",
        "jp": "JP",
        "kr": "KR",
        
    },
    "xtts-v2": {
        "english": "en",
        "en": "en",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "pt": "pt",
        "pl": "pl",
        "tr": "tr",
        "ru": "ru",
        "nl": "nl",
        "cs": "cs",
        "ar": "ar",
        "zh": "zh",
        "hu": "hu",
        "ko": "ko",
        "hi": "hi",
   
    }
}

def analyze_prompt_language_detect(input_text: str) -> str:
    """
    Detects the language of the input text using OpenAI and returns a normalized code.
    """
    system_prompt = f"""
    Identify the language of this text. Respond only with its name (e.g., English, Spanish, French):
    Text: "{input_text}"
    """

    if USE_GEMINI:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        response = model.generate_content(system_prompt)
        return response.text.strip().lower()
    else:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=5,
            temperature=0
        )
        return response.choices[0].message.content.strip().lower()

def map_language_for_model(model_name: str, detected_language: str) -> str:
    """
    Maps the detected language name/code to the correct format for the selected model.
    """
    language_map = LANGUAGE_DATABASE.get(model_name, {})
    return language_map.get(detected_language, "en")  # Default fallback

def create_voice_to_voice_prediction(
    model_name: str,
    input_text: str,
    audio_file_url: str
) -> str:
    """
    Creates a voice-to-voice synthesis prediction for the specified model.
    """
    if model_name not in ["openvoice", "xtts-v2"]:
        raise ValueError("Unsupported model. Use 'openvoice' or 'xtts-v2'.")

    # Detect and map language
    detected_language = analyze_prompt_language_detect(input_text)
    mapped_language = map_language_for_model(model_name, detected_language)

    input_payload = {
        "text": input_text,
        "language": mapped_language
    }

    if model_name == "openvoice":
        input_payload.update({
            "audio": audio_file_url,
            "speed": 1
        })
    elif model_name == "xtts-v2":
        input_payload.update({
            "speaker": audio_file_url,
            "cleanup_voice": False
        })

    payload = {
        "model": model_name,
        "version": "0.0.1",
        "input": input_payload,
        "webhook_url": ""
    }

    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json=payload
    )
    prediction = response.json()

    if prediction.get("status") != "success":
        raise Exception(f"Prediction failed: {prediction}")

    return prediction["predictionID"]
