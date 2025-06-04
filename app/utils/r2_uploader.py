# app/utils/r2_uploader.py
import boto3
from botocore.client import Config

# R2 credentials
ACCESS_KEY = '6be3de2c9f2d977313fc016e5161810c'
SECRET_KEY = '7ca8ec9a3bd94048d73050b6f4550cb924caa58a1629cb734290ab3055d00436'
ACCOUNT_ID = '0565d09d8a391bdf530fbe0f81c1233f'
BUCKET_NAME = 'harmonimgbucket'
# Endpoint used by boto3 (for uploading)
ENDPOINT_URL = f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com'

# Public URL format (for returning to user)

# Public URL base (used for returning to frontend)
PUBLIC_BASE_URL = f'https://{BUCKET_NAME}.r2.cloudflarestorage.com'

def upload_to_r2(file_bytes: bytes, object_key: str) -> str:
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
