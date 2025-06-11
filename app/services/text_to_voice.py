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


# Load environment variables
load_dotenv(override=True)

# Initialize API clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
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

def analyze_prompt(prompt,platform: str):
    """
    Analyzes the prompt to detect voice type, language, and the exact portion for audio conversion.
    Returns structured output in JSON format.
    """
    system_message = """
        You are a prompt analyzer for a text-to-speech (TTS) generation system.

        Your job is to extract clean, voice-ready content from a user's and return metadata in a valid JSON format.

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

            Examples:

            Input:
            a man says "who are you when you come"

            Output:
            {
                "audio-prompt": "who are you when you come",
                "voicetype": "male",
                "language": "english"
            }

            Input:
            Generate a girl’s voice to say something like: “Hello, and welcome to our Python basics class.”

            Output:
            {
                "audio-prompt": "Hello, and welcome to our Python basics class.",
                "voicetype": "female",
                "language": "english"
            }

            Input:
            Create an excited child voice saying something fun.

            Output:
            {
                "audio-prompt": "Let's go on an adventure! It's going to be so much fun!",
                "voicetype": "child",
                "language": "english"
            }
            Input : 
            a man says who are you when you come and then he says I am a
            Output :
            {
                "audio-prompt": "who are you when you come and then he says I am a
                ",
                "voicetype": "male",
                "language": "english"
            }
        """
    platform = platform.upper()

    try:
        if platform == "CHATGPT":
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            result = response.choices[0].message.content.strip()

        elif platform == "GEMINI":
            gemini_chat = genai.GenerativeModel("gemini-pro").start_chat()
            result = gemini_chat.send_message(f"{system_message}\n\n{prompt}").text.strip()

        elif platform == "GROK":
            raise NotImplementedError("Grok platform not supported yet — no public SDK available.")

        else:
            raise ValueError(f"Unsupported platform: {platform}")

        print(f"Analysis response ({platform}): {result}")
        return json.loads(result)

    except Exception as e:
        print(f"[{platform}] Prompt analysis failed: {e}")
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

def text_to_audio_generate(user_prompt :str):
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
            return url
        else:
            raise Exception("Audio generation failed: No output URL found.")
    except Exception as e:
        print(f"Error while fetching prediction: {e}")
        return None
