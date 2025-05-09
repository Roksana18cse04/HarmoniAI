import requests
import time
import os
from app.schemas.text_to_audio import TextToAudioRequest
import json
from openai import OpenAI
from dotenv import load_dotenv
import re


# Load environment variables
load_dotenv(override=True)

# Initialize OpenAI client with the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

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

def analyze_prompt(prompt):
    """
    Analyzes the prompt to detect voice type, language, and the exact portion for audio conversion.
    Returns structured output in JSON format.
    """
    system_message = """
    Analyze the following user prompt and provide a response in the following format:

    {
        "audio-prompt": "The extracted portion for audio conversion",
        "voicetype": "Detected voice type (male/female/child)",
        "language": "Detected language"
    }

    Ensure the response is in valid JSON format.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        message_content = response.choices[0].message.content.strip()
        print(f"Analysis response: {message_content}")  # Debugging line
        return json.loads(message_content)
    except Exception as e:
        print(f"Error analyzing prompt: {e}")
        # Default to English and male if analysis fails
        return {
            "audio-prompt": prompt,
            "voicetype": "male",
            "language": "english"
        }

def create_prediction(model_name, user_prompt):
    """
    Creates the prediction request payload based on model and user inputs.
    """
    analysis_result = analyze_prompt(user_prompt)
    voice_type = analysis_result.get('voicetype', 'male').lower()  # Default to 'male' if not provided
    language = analysis_result.get('language', 'english')
    audio_prompt = analysis_result.get('audio-prompt', user_prompt)

    # Retrieve the voice_id from the VOICE_DATABASE
    voice_id = None
    for voice_category, voices in VOICE_DATABASE.items():
        if voice_category == voice_type:
            voice_id = list(voices.values())[0]  # Use the first voice ID in the category
            break

    if not voice_id:
        print(f"Voice type '{voice_type}' not recognized. Defaulting to 'male'.")
        voice_id = list(VOICE_DATABASE["male"].values())[0]  # Default to the first male voice ID

    payload = {
        "model": model_name,
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

def get_prediction_result(prediction_id):
    """
    Polls the prediction result until it's ready.
    """
    while True:
        try:
            response = requests.get(
                f"https://api.eachlabs.ai/v1/prediction/{prediction_id}",
                headers=HEADERS
            )
            response.raise_for_status()
            result = response.json()

            if result["status"] == "success":
                return result
            elif result["status"] == "error":
                raise Exception(f"Prediction failed: {result}")
            else:
                print("Prediction is still processing, waiting...")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

        time.sleep(1)

def text_to_audio_generate(audio_request: TextToAudioRequest):
    """
    Generates audio based on the selected model and text.
    """
    try:
        prediction_id = create_prediction(audio_request.model_name, audio_request.prompt)
        print(f"Prediction ID: {prediction_id}")  # Debugging line

        audio_result = get_prediction_result(prediction_id)
        url = audio_result.get("output")

        if url:
            print(f"Audio generated successfully: {url}")
            return url
        else:
            raise Exception("Audio generation failed: No output URL found.")
    except Exception as e:
        print(f"Error while fetching prediction: {e}")
        return None

# Example usage
if __name__ == "__main__":
    audio_request = TextToAudioRequest(
        prompt=input("Enter the text for audio generation: "),
        model_name=input("Enter the model name ('kokoro-82m' or 'eleven-multilingual-v2'): ")
    )
    try:
        audio_url = text_to_audio_generate(audio_request)
        if audio_url:
            print(f"Generated audio URL: {audio_url}")
        else:
            print("Failed to generate audio.")
    except Exception as e:
        print(f"Error: {e}")
