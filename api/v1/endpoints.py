from fastapi import APIRouter
from models.input_schema import  DocumentInput, QueryInput
from services.generate_embedding_service import generate_embedding
from services.query_embedding_service import generate_answer

router = APIRouter()

@router.post("/embed")
def embed_content(doc: DocumentInput):
    return generate_embedding(doc)

@router.post("/query")
def query_rag(question:QueryInput):
    return generate_answer(question)