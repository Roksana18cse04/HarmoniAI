# app/config.py

import cloudinary
import os

class config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # C:\Users\Softvence\Documents\New folder (2)\Harmoni-AI\app
    DATA_PATH = os.path.join(BASE_DIR, "data")
    IMAGE_PATH= os.path.join(DATA_PATH, "image")


# Configure Cloudinary
cloudinary.config(
    cloud_name="dhubxnqvq",
    api_key="191483941177317",
    api_secret="_UxT7j99p2LnLZwAHznk4HlSFnw"
)