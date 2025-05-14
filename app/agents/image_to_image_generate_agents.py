import requests
import os
from app.schemas.Image_To_Image import ImageToImageRequest
from dotenv import load_dotenv
from app.services.image_to_image_create_Prediction import create_prediction ,get_prediction

# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def image_to_generate_image(image_request: ImageToImageRequest) -> dict:
    """
    Generate an image using the Each Labs API.

    Args:
        image_request (ImageToImageRequest): The request object containing image generation parameters.

    Returns:
        dict: A dictionary containing the prompt and the generated image URL, or None if the generation failed.
    """
    try:
        # Use the image_url already provided (uploaded to Cloudinary in the route)
        prediction_id = create_prediction(
        image_request.model_name,
        image_request.prompt,
        image_request.reference_image,  # Change from image_url
        image_request.style_slug
        )
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        result = get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    

if __name__ == "__main__":
    # Example input
    image_request = ImageToImageRequest(
        model_name="eachlabs-couple",
        prompt="A women image in the style of Ghibli anime",
        image_url="https://res.cloudinary.com/dhubxnqvq/image/upload/v1746779379/bnmo1abwxjmsxt6tsjdm.jpg",
        style_slug="ghibli-anime"
    )

    # Generate image and get result
    result = image_to_generate_image(image_request)

    # Print the result in the specified format
    print(result)
