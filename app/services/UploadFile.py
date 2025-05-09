from app.config import cloudinary
import cloudinary.uploader

def upload_image_to_cloudinary(image_path, folder="image"):
    upload_result = cloudinary.uploader.upload(image_path, folder=folder)
    return upload_result["secure_url"]