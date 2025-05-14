from fastapi import FastAPI, requests
from app.routes.models_selector import router as models_selector_router
from app.routes.image_generator_route import router as image_generator_router
from app.routes.prompt_enhance_routes import enhance_router as enhance__prompt_router
from app.routes.audio_videoRoute import router as audio_video_router


app = FastAPI(title="Multi-Agent System")

app.include_router(models_selector_router, prefix="/models-selector", tags=["models_selector"])
app.include_router(enhance__prompt_router, prefix="/enhance-prompt", tags=["enhance-prompt"])
app.include_router(image_generator_router, prefix="/image-generator", tags=["image-generator"])
app.include_router(audio_video_router, prefix="/video-generate", tags=["video-generate"])

# app.include_router(image_generator_router, prefix="/image-to-image-generator", tags=["image-to-image-generator"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Agent System!"}


