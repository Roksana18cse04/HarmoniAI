import requests
import time
import os
from dotenv import load_dotenv
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

def get_voice_id(voice_type, voice_name):
    """Get the voice ID from the VOICE_DATABASE based on user input."""
    try:
        return VOICE_DATABASE[voice_type][voice_name]
    except KeyError:
        raise ValueError(f"Voice {voice_name} not found in {voice_type} category.")

def detect_voice_type(user_prompt):
    """Detect voice type based on user prompt."""
    if "female" in user_prompt.lower():
        return "female", "Aria"  # Default female voice
    elif "child" in user_prompt.lower():
        return "child", "River"  # Default child voice
    else:
        return "male", "Roger"  # Default male voice

def create_prediction(model_name, user_prompt):
    """Create prediction request payload based on model and user inputs."""
    voice_type, voice_name = detect_voice_type(user_prompt)  # Detect voice type dynamically
    voice_id = get_voice_id(voice_type, voice_name)  # Get dynamic voice ID

    prompt = f"""
    You are a voice generation model. Your task is to generate audio based on the user prompt.
    You can generate audio in multiple languages and accents.
    
    VOICE_DATABASE = {{
        "male": {{
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
        }},
        "female": {{
            "Aria": "9BWtsMINqrJLrRacOk9x",
            "Sarah": "EXAVITQu4vr4xnSDxMaL",
            "Laura": "FGY2WhTYpPnrIDTdsKH5",
            "Charlotte": "XB0fDUnXU5powFXDhCwa",
            "Alice": "Xb7hH8MSUJpSbSDYk0k2",
            "Matilda": "XrExE9yKIg1WjnnlVkGX",
            "Jessica": "cgSgspJ2msm6clMCkdW9",
            "Lily": "pFZP5JQG7iQjIQuC4Bku"
        }},
        "child": {{
            "River": "SAz9YHcvj6GT2YYXdXww",
            "Will": "bIHbv24MWmeRgasZH58o"
        }}
    }}

    Suppose example prompt : I want audio generation for a {voice_type}(eg.male, female) voice in {voice_name}(eg. english ,bangla  etc) language: "hello my dear besti, how are you doing today?"
    oututput: {{
        "prompt": "{user_prompt}"
        "audio":url: "https://example.com/audio.mp3",
    }}
    """

    if model_name == "eleven-multilingual-v2":
        payload = {
            "model": "eleven-multilingual-v2",
            "version": "0.0.1",
            "input": {
                "use_speaker_boost": False,
                "style": 0,
                "similarity_boost": 0.7,
                "stability": 0.5,
                "seed": 99999,
                "text": prompt,
                "voice_id": voice_id  # Dynamic voice_id based on user input
            }
        }
    elif model_name == "kokoro-82m":
        payload = {
            "model": "kokoro-82m",
            "version": "0.0.1",
            "input": {
                "text": prompt,
                "speed": 1,
                "voice": voice_id  # Dynamic voice_id based on user input
            }
        }
    else:
        raise ValueError("Invalid model name")

    # Make the API request
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json=payload
    )

    prediction = response.json()
    print(f"Prediction response: {prediction}")  # Debugging line
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    
    return prediction["predictionID"]

def get_prediction_result(prediction_id):
    """Poll the prediction result until it's ready."""
    while True:
        try:
            response = requests.get(
                f"https://api.eachlabs.ai/v1/prediction/{prediction_id}",
                headers=HEADERS
            ).json()
            print(f"Prediction response: {response}")  # Debugging line

            if response["status"] == "success":
                return response
            elif response["status"] == "error":
                raise Exception(f"Prediction failed: {response}")
            else:
                print("Prediction is still processing, waiting...")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

        time.sleep(1)  # Wait for 1 second before polling again

def generate_audio(model_name, user_prompt):
    """Generate audio based on the selected model and text."""
    try:
        # Create prediction
        prediction_id = create_prediction(model_name, user_prompt)
        print(f"Prediction created: {prediction_id}")
        
        # Get the result URL (audio file)
        audio_url = get_prediction_result(prediction_id)
        url = audio_url.get("output")
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
    model_name = input("Enter the model name ('kokoro-82m' or 'eleven-multilingual-v2'): ")
    user_prompt = input("Enter the text for audio generation: ")

    try:
        # Generate audio
        audio_url = generate_audio(model_name, user_prompt)
        if audio_url:
            print(f"Generated audio URL: {audio_url}")
        else:
            print("Failed to generate audio.")
    except Exception as e:
        print(f"Error: {e}")
