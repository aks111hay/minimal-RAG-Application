"""
Centralized application configuration.

All environment-driven settings live here, validated at startup via
pydantic-settings. This means the app fails fast with a clear error
message if required config (like GOOGLE_API_KEY) is missing, instead
of crashing later mid-request.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Google Gemini ---
    google_api_key: str = Field(..., alias="GOOGLE_API_KEY")
    embedding_model: str = Field(default="gemini-embedding-001", alias="EMBEDDING_MODEL")
    generation_model: str = Field(default="gemini-2.5-flash", alias="GENERATION_MODEL")

    # --- Vector store (Chroma) ---
    chroma_persist_dir: str = Field(default=str(DATA_DIR / "chroma_db"), alias="CHROMA_PERSIST_DIR")
    chroma_collection_name: str = Field(default="rag_collection", alias="CHROMA_COLLECTION_NAME")

    # --- Chat memory (SQLite) ---
    memory_db_path: str = Field(default=str(DATA_DIR / "chat_memory.sqlite3"), alias="MEMORY_DB_PATH")
    max_history_turns: int = Field(default=6, alias="MAX_HISTORY_TURNS")

    # --- Chunking ---
    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, alias="CHUNK_OVERLAP")

    # --- Retrieval ---
    vector_top_k: int = Field(default=10, alias="VECTOR_TOP_K")
    bm25_top_k: int = Field(default=10, alias="BM25_TOP_K")
    rerank_top_n: int = Field(default=4, alias="RERANK_TOP_N")
    cross_encoder_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2", alias="CROSS_ENCODER_MODEL"
    )
    rrf_k: int = Field(default=60, alias="RRF_K")  # Reciprocal Rank Fusion constant

    # --- App / CORS ---
    app_name: str = Field(default="Advanced RAG API", alias="APP_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cors_origins: list[str] = Field(default=["http://localhost:5173"], alias="CORS_ORIGINS")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we only parse env once per process."""
    return Settings()