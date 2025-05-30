import requests
import os
from app.schemas.Image_To_Image import DressTrialImageRequest
from dotenv import load_dotenv
from app.services.dress_trail import create_prediction_for_dress_trail
from app.services.image_get_prediction import get_prediction


# Load environment variables
load_dotenv(override=True)

API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
def dress_trial_agent(image_request: DressTrialImageRequest):

    """
    Generate a dress trial image using the Each Labs API.
    Args:
        image_request (DressTrialImageRequest): The request object containing dress trial parameters.
    Returns:

        dict: A dictionary containing the prompt and the generated image URL, or None if the generation failed.
    """
    try:
        # Use the image_url already provided (uploaded to Cloudinary in the route)
        prediction_id = create_prediction_for_dress_trail(image_request.cloth_image_url, image_request.human_image_url)
        print(f"Prediction created: {prediction_id}")

        # Get result
        result = get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Example input
    image_request = DressTrialImageRequest(
        cloth_image_url="https://res.cloudinary.com/dhubxnqvq/image/upload/v1748410442/ldmca9qotd3enzi21vvu.jpg",
        human_image_url="https://res.cloudinary.com/dhubxnqvq/image/upload/v1748410443/elwrn8fdpkpkeks0ph3w.jpg"
    )
    # Generate image and get result
    result = dress_trial_agent(image_request)
    # Print the result in the specified format
    print(result)
