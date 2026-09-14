import logging

from fastapi import APIRouter

from backend.models.schemas import DocumentInput, IngestResponse, PDFInput
from backend.services import ingestion_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["ingestion"])


@router.post("/embed", response_model=IngestResponse)
def embed_content(doc: DocumentInput):
    logger.info("Received /embed request for document id='%s'", doc.id)
    return ingestion_service.ingest_text(doc)


@router.post("/embed-document", response_model=IngestResponse)
def embed_document(doc: PDFInput):
    logger.info("Received /embed-document request for '%s'", doc.filepath)
    return ingestion_service.ingest_pdf(doc)