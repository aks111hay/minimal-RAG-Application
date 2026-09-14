"""
Generation service: turns a (question, chat history, retrieved context)
triple into a final answer, with an intermediate query-rewriting step
that makes multi-turn conversations actually work.

Why query rewriting matters: if a user asks "What's the refund window?"
and then follows up with "What about for digital products?", a raw
vector search on the follow-up alone has no idea what "What about" refers
to. We ask the LLM to fold chat history into a single, standalone search
query before retrieval ever runs.
"""

import logging

from fastapi import HTTPException

from backend.core.clients import ai_client
from backend.core.config import get_settings
from backend.models.schemas import ChatMessage, RetrievedChunk

logger = logging.getLogger(__name__)
settings = get_settings()

_REWRITE_PROMPT = """Given the conversation history and a follow-up question, \
rewrite the follow-up into a standalone question that contains all context \
needed to search a knowledge base, without changing its meaning. \
If the follow-up question is already standalone, return it unchanged. \
Respond with ONLY the rewritten question, no explanation.

Conversation history:
{history}

Follow-up question: {question}

Standalone question:"""

_ANSWER_PROMPT = """You are a helpful assistant answering questions based on retrieved \
document context and the ongoing conversation. Answer the question using ONLY the \
information in the context below. If the context doesn't contain the answer, say \
"I cannot find the answer in the provided documents." Be concise and cite which \
part of the context you used when relevant.

Conversation history:
{history}

Context:
{context}

Question: {question}
Answer:"""


def rewrite_query(question: str, history: list[ChatMessage]) -> str:
    if not history:
        return question

    history_text = "\n".join(f"{m.role.capitalize()}: {m.content}" for m in history)
    prompt = _REWRITE_PROMPT.format(history=history_text, question=question)

    try:
        response = ai_client.models.generate_content(
            model=settings.generation_model,
            contents=prompt,
        )
        rewritten = response.text.strip()
        logger.info("Rewrote query: '%s' -> '%s'", question, rewritten)
        return rewritten or question
    except Exception:  # noqa: BLE001
        # Query rewriting is an enhancement, not a hard dependency - fall
        # back to the raw question rather than failing the whole request.
        logger.exception("Query rewrite failed; falling back to original question")
        return question


def generate_answer(
    question: str, context_chunks: list[RetrievedChunk], history: list[ChatMessage]
) -> str:
    if context_chunks:
        context = "\n\n".join(f"[{c.id}] {c.text}" for c in context_chunks)
    else:
        context = "No relevant information found in documents."

    history_text = (
        "\n".join(f"{m.role.capitalize()}: {m.content}" for m in history)
        if history
        else "(no previous conversation)"
    )

    prompt = _ANSWER_PROMPT.format(history=history_text, context=context, question=question)

    try:
        response = ai_client.models.generate_content(
            model=settings.generation_model,
            contents=prompt,
        )
        return response.text
    except Exception as exc:  # noqa: BLE001
        logger.exception("Answer generation failed")
        raise HTTPException(status_code=502, detail=f"Generation error: {exc}") from exc