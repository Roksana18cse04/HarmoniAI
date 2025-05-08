from fastapi import FastAPI, requests
from app.routes.models_selector import router as models_selector_router

app = FastAPI(title="Multi-Agent System")

app.include_router(models_selector_router, prefix="/models-selector", tags=["models_selector"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Agent System!"}


