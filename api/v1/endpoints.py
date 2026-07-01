from fastapi import APIRouter
from models.input_schema import  DocumentInput, QueryInput,PDFInput
from services.generate_embedding_service import generate_embedding,generate_embedding_by_pdf
from services.query_embedding_service import generate_answer

router = APIRouter()

@router.post("/embed")
def embed_content(doc: DocumentInput):
    return generate_embedding(doc)

@router.post("/query")
def query_rag(question:QueryInput):
    return generate_answer(question)


@router.post("/embed-document")
def embed_document(doc:PDFInput):
    return generate_embedding_by_pdf(doc)
