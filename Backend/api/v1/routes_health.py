from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def home():
    return {"message": "Welcome to the Advanced RAG API"}


@router.get("/health")
def health():
    return {"status": "ok"}