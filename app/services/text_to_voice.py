import requests
import time
import os
import random
import json
from openai import OpenAI
from dotenv import load_dotenv
import re
import google.generativeai as genai
from app.services._get_prediction import get_prediction
from app.services.llm_provider import LLMProvider
from app.services.token_calculate import price_calculate


# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Voice database mapping (male, female, child voices)
VOICE_DATABASE = {
    "male": {
        "Roger": "CwhRBWXzGAHq8TQ4Fs17",
        "Charlie": "IKne3meq5aSn9XLyUdCD",
        "George": "JBFqnCBsd6RMkjVDRZzb",
        "Callum": "N2lVS1w4EtoT3dr4eOWO",
        "Liam": "TX3LPaxmHKxFdv7VOQHJ",
        "Eric": "cjVigY5qzO86Huf0OWal",
        "Chris": "iP95p4xoKVk53GoZ742B",
        "Brian": "nPczCjzI2devNBz1zQrb",
        "Daniel": "onwK4e9ZLuTAKqWW03F9",
        "Bill": "pqHfZKP75CvOlQylNhV4"
    },
    "female": {
        "Aria": "9BWtsMINqrJLrRacOk9x",
        "Sarah": "EXAVITQu4vr4xnSDxMaL",
        "Laura": "FGY2WhTYpPnrIDTdsKH5",
        "Charlotte": "XB0fDUnXU5powFXDhCwa",
        "Alice": "Xb7hH8MSUJpSbSDYk0k2",
        "Matilda": "XrExE9yKIg1WjnnlVkGX",
        "Jessica": "cgSgspJ2msm6clMCkdW9",
        "Lily": "pFZP5JQG7iQjIQuC4Bku"
    },
    "child": {
        "River": "SAz9YHcvj6GT2YYXdXww",
        "Will": "bIHbv24MWmeRgasZH58o"
    }
}
def analyze_prompt(prompt: str, platform: str) -> dict:
    """
    Analyzes the prompt to detect voice type, language, and the exact portion for audio conversion.
    Returns structured output in JSON format.
    """
    system_message = """
        You are a prompt analyzer for a text-to-speech (TTS) generation system.

        Your job is to extract clean, voice-ready content from a user's prompt and return metadata in a valid JSON format.

        Your response must follow this structure:

        {
            "audio-prompt": "<The exact sentence or quoted phrase that should be converted to speech (preferably quoted speech if available), max 2–3 clean sentences.>",
            "voicetype": "<Detected voice type: male | female | child. Default to 'female' if not specified.>",
            "language": "<Detected language (e.g., english, spanish). Default to 'english' if unclear.>"
        }

        Rules:
        - ✅ If the user prompt contains quoted text (like “...”, "..." or ‘...’), extract ONLY the quoted part for `audio-prompt`.
        - ✅ If there is no quoted text, extract up to 2–3 clean, complete sentences suitable for TTS.
        - ❌ Do not include instructions, metadata, or context text.
        - 🎯 Only include voice-appropriate, speakable content.
        - 🔁 Always return valid JSON. Do not include commentary or explanations outside the JSON.
    """

    try:
        llm = LLMProvider(platform)
        response_text = llm.generate_response(system_message, prompt)
        # Parse JSON safely
        parsed = json.loads(response_text)
        # Provide fallback defaults if keys missing
        audio_prompt = parsed.get("audio-prompt", prompt)
        voicetype = parsed.get("voicetype", "female")
        language = parsed.get("language", "english")

        return {
            "prompt":prompt,
            "audio-prompt": audio_prompt,
            "voicetype": voicetype,
            "language": language
        }

    except Exception as e:
        print(f"[{platform}] Prompt analysis failed: {e}")
        # Fallback default if analysis fails
        return {
            "audio-prompt": prompt,
            "voicetype": "female",
            "language": "english"
        }


def create_prediction(user_prompt,platform:str):
    """
    Creates the prediction request payload based on model and user inputs.
    """
    analysis_result = analyze_prompt(user_prompt,platform)
    voice_type = analysis_result.get('voicetype', 'male').lower()  # Default to 'male' if not provided
    language = analysis_result.get('language', 'english')
    audio_prompt = analysis_result.get('audio-prompt', user_prompt)

    # Retrieve the voice_id from the VOICE_DATABASE
    voice_id = None
    voices_in_category = VOICE_DATABASE.get(voice_type)

    if voices_in_category:
        voice_id = random.choice(list(voices_in_category.values()))
    else:
        print(f"Voice type '{voice_type}' not recognized. Defaulting to 'male'.")
        voice_id = random.choice(list(VOICE_DATABASE["male"].values()))

    payload = {
        "model": "eleven-multilingual-v2",
        "version": "0.0.1",
        "input": {
            "use_speaker_boost": False,
            "style": 0,
            "similarity_boost": 0.7,
            "stability": 0.5,
            "language": language,
            "seed": 99999,
            "text": audio_prompt,
            "voice_id": voice_id
        }
    }

    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json=payload
    )
    prediction = response.json()
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    return prediction["predictionID"]

def text_to_audio_generate(user_prompt :str,platform:str):
    """
    Generates audio based on the selected model and text.
    """
    try:
        prediction_id = create_prediction(user_prompt)
        print(f"Prediction ID: {prediction_id}")  # Debugging line

        audio_result = get_prediction(prediction_id)
        url = audio_result.get("output")

        if url:
            print(f"Audio generated successfully: {url}")
            return {
                "platform": platform,
                "audio": url               
            }
        else:
            raise Exception("Audio generation failed: No output URL found.")
    except Exception as e:
        print(f"Error while fetching prediction: {e}")
        return None
