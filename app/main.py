from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi_mcp import FastApiMCP
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
# ─────────────────────────────────────────────────────────────────────────────
# JWT Setup
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY= os.getenv("JWT_ACCESS_SECRET")
ALGORITHM = "HS256"

security = HTTPBearer()

# def verify_token(token: str):
#     try:
#         return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except JWTError:
#         return None

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    print("Header:", auth_header)

    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")

    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = auth_header

    try:
        payload = jwt.decode(token.strip(), SECRET_KEY, algorithms=[ALGORITHM])
        print("Payload:", payload)
        return payload
    except JWTError as e:
        print("JWT Error:", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    # token = credentials.credentials
    # payload = verify_token(token)
    # print("payload------------",payload)
    # if not payload:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid or expired token",
    #     )
    # return payload

# ─────────────────────────────────────────────────────────────────────────────
# App Setup


from app.services.media_content import fetch_all_media_async
from app.services.product_weaviate import fetch_all_products, fetch_all_products_async
from app.services.create_schema import setup_schema
from app.routes.execute_prompt_router import router as models_selector_router
from app.routes.text_image_generator_route import router as image_generator_router
from app.routes.image_to_video_routes import router as image_to_video_with_audio
from app.routes.prompt_enhance_routes import enhance_router as enhance_prompt_router

from app.routes.image_process import router as image_to_image_process
from app.routes.Audio_generate import router as audio_generate_router
from app.routes.video_to_text_route import router as video_to_text_router
from app.routes.merge_video_audio_routs import router as merge_video_audio_router
from app.routes.voice_cloning_route import router as voice_cloning_router
from app.routes.pdf_extract_routes import router as pdf_extract_router
from app.routes.text_to_video_routes import router as text_to_video_router
from app.routes.get_eachlabs_models import router as models_list_router

import uvicorn
import os
from fastapi_mcp import FastApiMCP
from app.services.weaviate_client import client

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Initialize only once
app = FastAPI(title="Multi-Agent System")
scheduler = AsyncIOScheduler()

# MCP setup
mcp = FastApiMCP(app)
mcp.mount()

# Routers
app.include_router(models_list_router, prefix="/models-list", tags=["get-models-list"], dependencies=[Depends(get_current_user)])
app.include_router(models_selector_router, prefix="/models-selector", tags=["prompt-handler"], dependencies=[Depends(get_current_user)])
app.include_router(enhance_prompt_router, prefix="/enhance-prompt", tags=["enhance-prompt"], dependencies=[Depends(get_current_user)])
app.include_router(image_generator_router, prefix="/image-generator", tags=["text-to-image"], dependencies=[Depends(get_current_user)])
app.include_router(image_to_video_with_audio, prefix="/image-to-video-add-audio", tags=["image-to-video-audio"], dependencies=[Depends(get_current_user)])
app.include_router(image_to_image_process, prefix="/image-process", tags=["image-to-image-process"], dependencies=[Depends(get_current_user)])
app.include_router(audio_generate_router, prefix="/audio-generate", tags=["text-to-voice"], dependencies=[Depends(get_current_user)])
app.include_router(video_to_text_router, prefix="/video-to-text", tags=["video-to-text"], dependencies=[Depends(get_current_user)])
app.include_router(voice_cloning_router, prefix="/voice-cloning", tags=["voice-to-voice"], dependencies=[Depends(get_current_user)])
app.include_router(pdf_extract_router, prefix="/pdf-to-text", tags=["pdf-to-text"], dependencies=[Depends(get_current_user)])
app.include_router(text_to_video_router, prefix="/text-to-video", tags=["text-to-video"], dependencies=[Depends(get_current_user)])
app.include_router(merge_video_audio_router, prefix="/merge-audio-video", tags=["merge-audio-video"], dependencies=[Depends(get_current_user)])

# Refresh MCP server to include all routes
mcp.setup_server()

# Weaviate client
weaviate_client = client
try:
    if weaviate_client.is_ready():
        print("Weaviate client connected successfully!")
    else:
        print("Weaviate client is not ready")
except Exception as e:
    print(f"Connection failed: {e}")

@app.on_event("startup")
async def startup_event():
    weaviate_client.connect()
    setup_schema()
    scheduler.add_job(fetch_all_media_async, 'interval', hours=6) 
    scheduler.add_job(fetch_all_products_async, 'interval', hours=6)
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    if weaviate_client is not None:
        scheduler.shutdown()
        weaviate_client.close()

# @app.get("/manual-refresh-product-embedding")
# async def manual_refresh():
#     fetch_all_products()
#     return {"message": "Product index refreshed manually!"}

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Agent System!"}

# Secure route with JWT
# @app.get("/secure-status")
# async def secure_status(user: dict = Depends(get_current_user)):
#     return {"message": "Secure access granted!", "user": user}

# Add BearerAuth to Swagger UI docs
from fastapi.openapi.utils import get_openapi
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="API with JWT Auth",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


def main():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    main()
