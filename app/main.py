from fastapi import FastAPI, requests
from app.routes.classify import router as classify_router

app = FastAPI(title="Multi-Agent System")

app.include_router(classify_router, prefix="/classify", tags=["classify"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Agent System!"}


