"""
Orchestrates a single conversational RAG turn:

  1. Load recent chat history for the session
  2. Rewrite the question into a standalone query using that history
  3. Hybrid retrieve + rerank relevant chunks using the rewritten query
  4. Generate an answer grounded in those chunks + history
  5. Persist the turn to chat memory

This is the module the API route calls; it has no knowledge of HTTP.
"""

import logging

from backend.models.schemas import QueryInput, QueryResponse
from backend.services import generation_service, memory_service, retrieval_service

logger = logging.getLogger(__name__)


def answer_question(payload: QueryInput) -> QueryResponse:
    history = memory_service.get_history(payload.session_id)

    rewritten_query = generation_service.rewrite_query(payload.question, history)

    retrieved_chunks = retrieval_service.hybrid_retrieve(rewritten_query, top_n=payload.top_k)

    answer = generation_service.generate_answer(payload.question, retrieved_chunks, history)

    memory_service.record_turn(payload.session_id, payload.question, answer)

    return QueryResponse(
        answer=answer,
        retrieved_docs=retrieved_chunks,
        rewritten_query=rewritten_query if rewritten_query != payload.question else None,
        session_id=payload.session_id,
    )