from fastapi import FastAPI, requests
from app.routes.classify import router as classify_router
from app.routes.prompt_enhance_routes import enhance_router as enhance__prompt_router

app = FastAPI(title="Multi-Agent System")

app.include_router(classify_router, prefix="/classify", tags=["classify"])
app.include_router(enhance__prompt_router, prefix="/enhance-prompt", tags=["enhance-prompt"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Agent System!"}


