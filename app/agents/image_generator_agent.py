import requests
import os
from app.schemas.TextToImage import TextToImageRequest
from dotenv import load_dotenv
from app.services.textToImage_create_prediction import create_prediction
from app.services._get_prediction import get_prediction
# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def text_to_generate_image(image_request: TextToImageRequest) -> dict:
    """
    Generate an image using the Each Labs API.

    Args:
        image_request (TextToImageRequest): The request object containing image generation parameters.

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
    image_request = TextToImageRequest(
        model_name="flux-dev-realism",
        prompt="A dog wearing a hat, in a cartoon style, colorful and fun",
        intend = "str"
    )

    # Generate image and get result
    result = text_to_generate_image(image_request)

    # Print the result in the specified format
    print(result)
