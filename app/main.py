from fastapi import FastAPI
from app.routes.execute_prompt_router import router as models_selector_router
from app.routes.image_generator_route import router as image_generator_router
from app.routes.audio_videoRoute import router as audio_video_router
from app.routes.prompt_enhance_routes import enhance_router as enhance_prompt_router
from app.routes.content_generator_route import router as content_creator_router
from app.services.media_content import fetch_all_media
from app.services.product_weaviate import fetch_and_index_all_products
from app.services.create_schema import setup_schema
from app.routes.image_process import router as image_to_image_process
from app.routes.style_get_route import router as style_get_router
from app.routes.Audio_generate import router as audio_generate_router
from app.routes.video_to_text_route import router as video_to_text_router
from app.routes.merge_video_audio_routs import router as merge_video_audio_router
from app.routes.voice_cloning_route import router as voice_cloning_router
from app.routes.pdf_extract_routes import router as pdf_extract_router
import uvicorn
import os

from app.services.weaviate_client import client

app = FastAPI(title="Multi-Agent System")

weaviate_client = client
# Test the connection
try:
    # Check if client is ready
    if weaviate_client.is_ready():
        print("Weaviate client connected successfully!")
    else:
        print("Weaviate client is not ready")
        
except Exception as e:
    print(f"Connection failed: {e}")

# from contextlib import asynccontextmanager
# import app.scheduler as scheduler
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     scheduler.start()  # Start your background job scheduler
#     yield
#     # (Optional) teardown logic goes here
# app = FastAPI(title="Multi-Agent System",lifespan=lifespan)

app = FastAPI(title="Multi-Agent System")

app.include_router(models_selector_router, prefix="/models-selector", tags=["prompt-handler"])
app.include_router(style_get_router,prefix="/model_name_slug",tags =["style_slug"])
app.include_router(enhance_prompt_router, prefix="/enhance-prompt", tags=["enhance-prompt"])
app.include_router(image_generator_router, prefix="/image-generator", tags=["image-generator"])
app.include_router(audio_video_router, prefix="/video-generate", tags=["video-generate"])
app.include_router(content_creator_router, prefix="/content-creator", tags=["content-create"])
app.include_router(image_to_image_process,prefix="/image-process",tags = ["/image-to-image-process"])
app.include_router(audio_generate_router,prefix = "/audio-generate",tags = ["/text-to-audio"])
app.include_router(video_to_text_router,prefix = "/video-to-text",tags = ["/video-to-text"])
app.include_router(voice_cloning_router,prefix = "/voice-cloning",tags = ["/voice_cloning"])
app.include_router(pdf_extract_router,prefix = "/pdf-to-text",tags = ["pdf extract"])
app.include_router(merge_video_audio_router,prefix="/merge-audio-video",tags=["merge-audio-video"])

@app.on_event("startup")
async def startup_event():
    setup_schema()
    fetch_all_media()
    

@app.on_event("shutdown")
async def shutdown_event():
    weaviate_client.close()

@app.get("/manual-refresh-product-embedding")
async def manual_refresh():
    fetch_and_index_all_products()
    return {"message": "Product index refreshed manually!"}


@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Agent System!"}


def main():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    main()