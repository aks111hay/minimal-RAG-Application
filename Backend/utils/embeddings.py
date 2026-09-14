"""
Thin wrapper around the Gemini embedding endpoint with logging and
consistent error handling.
"""

import logging

from fastapi import HTTPException

from backend.core.clients import ai_client
from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_embedding(text: str) -> list[float]:
    """Embed a single string. Raises HTTPException(502) on provider failure."""
    try:
        result = ai_client.models.embed_content(
            model=settings.embedding_model,
            contents=text,
        )
        return result.embeddings[0].values
    except Exception as exc:  # noqa: BLE001 - we want to wrap any provider error
        logger.exception("Embedding request failed")
        raise HTTPException(status_code=502, detail=f"Embedding error: {exc}") from exc


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Embed multiple strings. The Gemini SDK's embed_content accepts a list
    directly, which is far more efficient than one call per chunk.
    """
    if not texts:
        return []
    try:
        result = ai_client.models.embed_content(
            model=settings.embedding_model,
            contents=texts,
        )
        return [e.values for e in result.embeddings]
    except Exception as exc:  # noqa: BLE001
        logger.exception("Batch embedding request failed for %d texts", len(texts))
        raise HTTPException(status_code=502, detail=f"Embedding error: {exc}") from exc