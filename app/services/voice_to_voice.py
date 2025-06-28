import requests
import os
from dotenv import load_dotenv
from app.services.llm_provider import LLMProvider
from app.services.price_calculate import price_calculate

# Load environment variables
load_dotenv(override=True)
EACHLABS_API_KEY = os.getenv("EACHLABS_API_KEY")

HEADERS = {
    "X-API-Key": EACHLABS_API_KEY,
    "Content-Type": "application/json"
}

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

def analyze_prompt_language_detect(prompt, platform, llm_model) -> dict:
    system_prompt = """
    Identify the language of this text. Respond only with the language name (e.g., English, Spanish, French).
    """
    user_prompt = f'Text: "{prompt}"'

    llm = LLMProvider(platform, llm_model)
    response = llm.generate_response(system_prompt, user_prompt)

    if not isinstance(response, dict) or "content" not in response:
        raise ValueError("Invalid LLM response structure.")

    language_raw = response["content"]
    language_detect = language_raw.replace('\\', '').strip('"').strip()

    price = price_calculate(platform, llm_model, user_prompt, response)

    return {
        "detected_language": language_detect,
        "price": price['price'],
        "input_token": price['input_token'],
        "output_token": price['output_token']
    }

def map_language_for_model(model_name: str, detected_language: str) -> str:
    return LANGUAGE_DATABASE.get(model_name, {}).get(detected_language.lower(), "en")

def create_voice_to_voice_prediction(platform, prompt, audio_file_url, llm_model, eachlabs_model_name):
    if eachlabs_model_name not in ["openvoice", "xtts-v2"]:
        raise ValueError("Unsupported model. Use 'openvoice' or 'xtts-v2'.")

    detected_language_info = analyze_prompt_language_detect(prompt, platform, llm_model)
    price_details = {
        "input_token": detected_language_info["input_token"],
        "output_token": detected_language_info["output_token"],
        "price": detected_language_info["price"]
    }
    detected_language = detected_language_info["detected_language"]
    mapped_language = map_language_for_model(eachlabs_model_name, detected_language)

    input_payload = {
        "text": prompt,
        "language": mapped_language
    }

    if eachlabs_model_name == "openvoice":
        input_payload.update({"audio": audio_file_url, "speed": 1})
    elif eachlabs_model_name == "xtts-v2":
        input_payload.update({"speaker": audio_file_url, "cleanup_voice": False})

    payload = {
        "model": eachlabs_model_name,
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

    return prediction, payload, price_details