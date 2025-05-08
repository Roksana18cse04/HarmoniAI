import requests
import time
import os
from app.config import ImageRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def create_prediction(prompt: str,model_name : str) -> str:
    """
    Create a prediction request to the Each Labs API.

    Args:
        prompt (str): The text prompt for image generation.

    Returns:
        str: The prediction ID.
    """
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": model_name,
            "version": "0.0.1",
            "input": {
                "prompt": prompt,
                "guidance": 3.5,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "webp",
                "output_quality": 80,
                "prompt_strength": 0.8,
                "num_inference_steps": 28
            }
        }
    )
    response.raise_for_status()
    prediction = response.json()
    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")
    return prediction["predictionID"]

def get_prediction(prediction_id: str) -> str:
    """
    Poll the Each Labs API for the prediction result.

    Args:
        prediction_id (str): The ID of the prediction to poll.

    Returns:
        str: URL of the generated image or None if the generation failed.
    """
    try:
        while True:
            response = requests.get(
                f"https://api.eachlabs.ai/v1/prediction/{prediction_id}",
                headers=HEADERS
            )
            response.raise_for_status()
            result = response.json()

            # Print the full response to understand its structure
            print("Response:", result)

            if isinstance(result, dict) and result.get("status") == "success":
                if "output" in result and isinstance(result["output"], list):
                    image_url = result["output"][0]  # Access the first URL in the list
                    print(f"Image generation successful: {image_url}")
                    return image_url
                else:
                    print("Error: 'output' not found or not a list.")
                    return None
            elif result.get("status") in ["error", "cancelled"]:
                print(f"Error: {result.get('message', 'Generation failed')}")
                return None

            print("Processing...")
            time.sleep(3)

    except requests.exceptions.RequestException as e:
        print(f"Error polling prediction: {e}")
        return None


def generate_image(image_request: ImageRequest) -> dict:
    """
    Generate an image using the Each Labs API.

    Args:
        image_request (ImageRequest): The request object containing image generation parameters.

    Returns:
        dict: A dictionary containing the prompt and the generated image URL, or None if the generation failed.
    """
    try:
        # Create prediction and get prediction ID
        prediction_id = create_prediction(image_request.prompt, image_request.model_name)
        
        # Get the image URL
        image_url = get_prediction(prediction_id)

        # If an image URL was returned, return the prompt and the image URL
        if image_url:
            return {"prompt": image_request.prompt, "image_url": image_url}
        else:
            return {"prompt": image_request.prompt, "image_url": None}
    except Exception as e:
        # Handle any errors during the process
        print(f"Error generating image: {e}")
        return {"prompt": image_request.prompt, "image_url": None}


if __name__ == "__main__":
    # Example input
    image_request = ImageRequest(
        model_name="flux-1.1-pro",
        prompt="A dog wearing a hat, in a cartoon style, colorful and fun"
    )

    # Generate image and get result
    result = generate_image(image_request)

    # Print the result in the specified format
    print(result)
