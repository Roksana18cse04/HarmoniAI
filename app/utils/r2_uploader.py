# app/utils/r2_uploader.py

import boto3
from botocore.client import Config
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Secure configuration via environment variables
ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
SECRET_KEY = os.getenv("R2_SECRET_KEY")
REGION = os.getenv("R2_REGION", "auto")
BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
PUBLIC_BASE_URL = os.getenv("R2_PUBLIC_BASE_URL")  # e.g., https://cdn.harmoniai.net

def upload_to_r2(file_bytes: bytes, object_key: str) -> str:
    """
    Uploads a file to R2 and returns the public URL.

    :param file_bytes: File content in bytes
    :param object_key: Path/key in the bucket (e.g., 'images/output.png')
    :return: Public URL of the uploaded file
    """
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        endpoint_url=ENDPOINT_URL,
        config=Config(signature_version='s3v4'),
    )

    s3.put_object(Bucket=BUCKET_NAME, Key=object_key, Body=file_bytes)

    return f"{PUBLIC_BASE_URL}/{object_key}"

# # Local test block
# if __name__ == "__main__":
#     test_data = b"Hello, world!"
#     test_key = "test/test.txt"
#     public_url = upload_to_r2(test_data, test_key)
#     print("Uploaded to:", public_url)
