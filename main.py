from fastapi import FastAPI
from api.v1.endpoints import router as v1_router
app = FastAPI(title="Minimal Gemini RAG API")
app.include_router(v1_router)

@app.get("/")
def home():
    return {"message":"welcome to my RAG Application"}

@app.get("/health")
def health():
    return {"message":"service is running"}
