# app/config.py
import os





# Set up directories
AUDIO_DIR = "app/data/audio"
VIDEO_DIR = "app/data/video"
OUTPUT_DIR_VIDEO = "app/data/output_video"
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR_VIDEO, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "data.json")


class config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # C:\Users\Softvence\Documents\New folder (2)\Harmoni-AI\app
    DATA_PATH = os.path.join(BASE_DIR, "data")
    IMAGE_PATH= os.path.join(DATA_PATH, "image")



