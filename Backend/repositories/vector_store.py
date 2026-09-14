"""
Repository layer around ChromaDB. Isolates the rest of the app from
Chroma's API shape so the underlying vector DB could be swapped
(e.g. for Qdrant/Pgvector) without touching service logic.
"""

import logging

from backend.core.clients import collection

logger = logging.getLogger(__name__)


def add_documents(
    ids: list[str],
    embeddings: list[list[float]],
    documents: list[str],
    metadatas: list[dict] | None = None,
) -> None:
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    logger.info("Added %d document(s) to vector store", len(ids))


def query_by_embedding(embedding: list[float], top_k: int) -> dict:
    return collection.query(query_embeddings=[embedding], n_results=top_k)


def get_all_documents() -> dict:
    """
    Fetch every stored document (id + text) for BM25 indexing.
    Fine for small/medium corpora; for very large corpora this should be
    replaced with a persisted BM25 index built incrementally at ingest time.
    """
    return collection.get(include=["documents", "metadatas"])