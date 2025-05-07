import requests
import json
import os
from dotenv import load_dotenv
load_dotenv(override=True)

EACHLABS_API_KEY = os.getenv("EACHLABS_API_KEY")



def fetch_models_by_category_id(category_id: int):
    url = "https://api.eachlabs.ai/v1/models"
    headers = {
        "X-API-Key": EACHLABS_API_KEY
    }
    response = requests.get(url, headers=headers)
    print("response:------------------", response)
    if response.status_code == 200:
        models = response.json()["data"]
        print("models:------------------", models)
    else:
        raise Exception(f"Error: {response.status_code} {response.text}")

    # print("Eachlabs API Key:------------------", EACHLABS_API_KEY)

    # BASE_URL = f"https://api.eachlabs.ai/v1/prediction/{category_id}"
    # print("BASE_URL:------------------", BASE_URL)
    # headers = {
    #     "X-API-Key": EACHLABS_API_KEY,
    #     "Content-Type": "application/json"
    # }
    # response = requests.get(BASE_URL, headers=headers)
    
    # if response.status_code == 200:
    #     data = response.json()
    #     print("data:------------------", data)
    
    #     return data
    # else:
    #     raise Exception(f"Error fetching tools: {response.status_code} {response.text}")

# import requests
# import time
# import os
# from dotenv import load_dotenv
# load_dotenv(override=True)

# API_KEY =  os.getenv("EACHLABS_API_KEY")
# HEADERS = {
#     "X-API-Key": API_KEY,
#     "Content-Type": "application/json"
# }

# def create_prediction():
#     response = requests.post(
#         "https://api.eachlabs.ai/v1/prediction/",
#         headers=HEADERS,
#         json={
#             "model": "action-figure-generator",
#             "version": "0.0.1",
#             "input": {
#   "image_url_1": "https://storage.googleapis.com/magicpoint/models/man.png",
#   "style_slug": "digital-nomad"
# }
#         }
#     )
#     prediction = response.json()
#     if prediction["status"] != "success":
#         raise Exception(f"Prediction failed: {prediction}")
#     return prediction["predictionID"]


# def get_prediction(prediction_id):
#     while True:
#         result = requests.get(
#             f"https://api.eachlabs.ai/v1/prediction/{prediction_id}",
#             headers=HEADERS
#         ).json()
        
#         if result["status"] == "success":
#             return result
#         elif result["status"] == "error":
#             raise Exception(f"Prediction failed: {result}")
        
#         time.sleep(1)  # Wait before polling again

# def fetch_models_by_category_id(category_id: int):
#     try:
#         # Create prediction
#         prediction_id = create_prediction()
#         print(f"Prediction created: {prediction_id}")
        
#         # Get result
#         result = get_prediction(prediction_id)
#         print(f"Output URL: {result['output']}")
#         print(f"Processing time: {result['metrics']['predict_time']}s")
#     except Exception as e:
#         print(f"Error: {e}")

