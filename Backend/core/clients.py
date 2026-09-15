"""
Singletons for external clients: the Gemini API client and the Chroma
vector store client. Kept separate from business logic so services can
be unit-tested by mocking these two objects.
"""

import logging

import chromadb
from google import genai

from backend.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

ai_client = genai.Client(api_key=settings.google_api_key)

chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
collection = chroma_client.get_or_create_collection(
    name=settings.chroma_collection_name,
    metadata={"hnsw:space": "cosine"},
)

logger.info(
    "Initialized Chroma collection '%s' at '%s'",
    settings.chroma_collection_name,
    settings.chroma_persist_dir,
)