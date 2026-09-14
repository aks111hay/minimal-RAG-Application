"""
Ingestion service: turns raw text or a PDF file into chunked, embedded
entries in the vector store. This replaces generate_embedding_service.py
with clearer separation, batch embedding, and fixed error handling.
"""

import logging
import os

from fastapi import HTTPException
from pypdf import PdfReader

from backend.core.config import get_settings
from backend.models.schemas import DocumentInput, IngestResponse, PDFInput
from backend.repositories import vector_store
from backend.utils.chunking import split_text_into_chunks
from backend.utils.embeddings import get_embedding, get_embeddings_batch

logger = logging.getLogger(__name__)
settings = get_settings()


def ingest_text(doc: DocumentInput) -> IngestResponse:
    """Embed and store a single, caller-chunked piece of text as-is."""
    vector = get_embedding(doc.text)
    vector_store.add_documents(ids=[doc.id], embeddings=[vector], documents=[doc.text])
    logger.info("Embedded raw document '%s'", doc.id)
    return IngestResponse(status="success", message=f"Document '{doc.id}' successfully embedded", chunks_created=1)


def ingest_pdf(input_pdf: PDFInput) -> IngestResponse:
    """Extract text from a PDF, chunk it, embed in batch, and store."""
    if not os.path.exists(input_pdf.filepath):
        raise HTTPException(status_code=404, detail="File path not found")

    try:
        reader = PdfReader(input_pdf.filepath)
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to read PDF '%s'", input_pdf.filepath)
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {exc}") from exc

    if not full_text.strip():
        raise HTTPException(status_code=400, detail="PDF appears to be empty or unreadable")

    chunks = split_text_into_chunks(full_text, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks produced from PDF text")

    try:
        vectors = get_embeddings_batch(chunks)

        source_name = os.path.basename(input_pdf.filepath)
        ids = [f"{source_name}_chunk_{idx}" for idx in range(len(chunks))]
        metadatas = [
            {"source": input_pdf.filepath, "chunk_index": idx} for idx in range(len(chunks))
        ]

        vector_store.add_documents(ids=ids, embeddings=vectors, documents=chunks, metadatas=metadatas)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to embed/store PDF chunks for '%s'", input_pdf.filepath)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {exc}") from exc

    logger.info("Ingested PDF '%s' as %d chunks", source_name, len(chunks))
    return IngestResponse(
        status="success",
        message=f"Successfully processed '{source_name}' into {len(chunks)} chunks.",
        chunks_created=len(chunks),
    )