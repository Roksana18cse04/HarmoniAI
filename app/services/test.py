import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import google.generativeai as genai


# Load environment variables
load_dotenv(override=True)

# Initialize API clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EACHLABS_API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": EACHLABS_API_KEY,
    "Content-Type": "application/json"
}

openai_client = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# Language database
LANGUAGE_DATABASE = {
    "openvoice": {
        "english": "EN", "en": "EN", "es": "ES", "fr": "FR", "zh": "ZH", "jp": "JP", "kr": "KR",
    },
    "xtts-v2": {
        "english": "en", "en": "en", "es": "es", "fr": "fr", "de": "de", "it": "it", "pt": "pt",
        "pl": "pl", "tr": "tr", "ru": "ru", "nl": "nl", "cs": "cs", "ar": "ar", "zh": "zh",
        "hu": "hu", "ko": "ko", "hi": "hi"
    }
}
def analyze_prompt_language_detect(input_text: str, platform: str) -> str:
    """
    Detects the language of the input text using selected platform.
    """
    system_prompt = f"""
    Identify the language of this text. Respond only with its name (e.g., English, Spanish, French):
    Text: "{input_text}"
    """
    platform = platform.upper()
    if platform == "GEMINI":
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        response = model.generate_content(system_prompt)
        return response.text.strip().lower()

    elif platform =="CHATGPT":
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=5,
            temperature=0
        )
        return response.choices[0].message.content.strip().lower()

    elif platform == "GROK":
        raise NotImplementedError("Grok support is not yet implemented.")


def map_language_for_model(model_name: str, detected_language: str) -> str:
    return LANGUAGE_DATABASE.get(model_name, {}).get(detected_language.lower(), "en")

def create_voice_to_voice_prediction(
    model_name: str,
    input_text: str,
    audio_file_url: str,
    platform: str
) -> str:
    """
    Creates a voice-to-voice synthesis prediction for the specified model.
    """
    if model_name not in ["openvoice", "xtts-v2"]:
        raise ValueError("Unsupported model. Use 'openvoice' or 'xtts-v2'.")

    # Detect and map language
    detected_language = analyze_prompt_language_detect(input_text, platform)
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
