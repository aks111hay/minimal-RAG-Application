"""
Request/response contracts for the API. Kept separate from business
logic (services) so the API surface can evolve independently.
"""

from pydantic import BaseModel, Field


# ---------- Ingestion ----------

class DocumentInput(BaseModel):
    id: str = Field(..., description="Caller-supplied unique ID for this document/chunk")
    text: str = Field(..., min_length=1, description="Raw text content to embed and store")


class PDFInput(BaseModel):
    filepath: str = Field(..., description="Path to a PDF file accessible on the server")


class IngestResponse(BaseModel):
    status: str
    message: str
    chunks_created: int = 0


# ---------- Query ----------

class QueryInput(BaseModel):
    question: str = Field(..., min_length=1, description="User's natural-language question")
    session_id: str = Field(
        default="default",
        description="Conversation/session identifier used to look up and store chat history",
    )
    top_k: int | None = Field(
        default=None, description="Override number of chunks used as context (advanced use)"
    )


class RetrievedChunk(BaseModel):
    id: str
    text: str
    source: str | None = None
    score: float | None = None


class QueryResponse(BaseModel):
    answer: str
    retrieved_docs: list[RetrievedChunk]
    rewritten_query: str | None = None
    session_id: str


# ---------- Chat history ----------

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessage]