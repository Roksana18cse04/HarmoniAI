import requests
import os
from dotenv import load_dotenv

# Load API keys
load_dotenv(override=True)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Your EachLabs workflow ID
WORKFLOW_ID = "92ef0655-b3d9-49f2-b717-d3a8174f1b42"

def generate_video_with_sound(prompt: str, duration: int, webhook_url: str = "") -> dict:
    """
    Calls EachLabs video generation API with prompt and duration.

    Args:
        prompt (str): Text prompt for video generation.
        duration (int): Duration in seconds.
        webhook_url (str): Optional webhook to notify when done.

    Returns:
        dict: Response from EachLabs
    """
    response = requests.post(
        f"https://flows.eachlabs.ai/api/v1/{WORKFLOW_ID}/trigger",
        headers=HEADERS,
        json={
            "parameters": {
                "prompt": prompt,
                "duration": duration
            },
            "webhook_url": webhook_url,
        },
    )

    try:
        return response.text
    except Exception as e:
        return {"error": str(e), "raw_response": response.text}

if __name__ == "__main__":
    # Example usage
    prompt = "A futuristic cityscape with flying cars and robots and talk to her speed"
    duration = 60  # seconds
    response = generate_video_with_sound(prompt, duration)
    print(response)