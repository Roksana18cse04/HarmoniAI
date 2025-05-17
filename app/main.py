from fastapi import FastAPI
from app.routes.execute_prompt_router import router as models_selector_router
from app.routes.image_generator_route import router as image_generator_router

from app.routes.audio_videoRoute import router as audio_video_router
from app.routes.prompt_enhance_routes import enhance_router as enhance_prompt_router
from app.routes.content_generator_route import router as content_creator_router
from app.routes.caption_generator_route import router as caption_generator_router

from app.services.xml_to_faiss import fetch_and_index_all_products

# from contextlib import asynccontextmanager
# import app.scheduler as scheduler
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     scheduler.start()  # Start your background job scheduler
#     yield
#     # (Optional) teardown logic goes here
# app = FastAPI(title="Multi-Agent System",lifespan=lifespan)

app = FastAPI(title="Multi-Agent System")

app.include_router(models_selector_router, prefix="/models-selector", tags=["models_selector"])
app.include_router(enhance_prompt_router, prefix="/enhance-prompt", tags=["enhance-prompt"])
app.include_router(image_generator_router, prefix="/image-generator", tags=["image-generator"])
app.include_router(audio_video_router, prefix="/video-generate", tags=["video-generate"])
app.include_router(content_creator_router, prefix="/content-creator", tags=["content-create"])
app.include_router(caption_generator_router,prefix="/caption-generator", tags=["/caption-generate"])

@app.get("/manual-refresh-product-embedding")
async def manual_refresh():
    fetch_and_index_all_products()
    return {"message": "Product index refreshed manually!"}

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Agent System!"}


