"""
Conversational memory service. Wraps the SQLite repository with the
app's configured history window and exposes a clean interface to the
rest of the app (retrieval/generation services, API routes).
"""

import logging

from backend.core.config import get_settings
from backend.models.schemas import ChatMessage
from backend.repositories import memory_store

logger = logging.getLogger(__name__)
settings = get_settings()


def get_history(session_id: str) -> list[ChatMessage]:
    rows = memory_store.get_recent_messages(session_id, settings.max_history_turns)
    return [ChatMessage(**row) for row in rows]


def record_turn(session_id: str, user_message: str, assistant_message: str) -> None:
    memory_store.add_message(session_id, "user", user_message)
    memory_store.add_message(session_id, "assistant", assistant_message)


def clear_history(session_id: str) -> None:
    memory_store.clear_session(session_id)


def format_history_for_prompt(history: list[ChatMessage]) -> str:
    if not history:
        return "(no previous conversation)"
    lines = [f"{msg.role.capitalize()}: {msg.content}" for msg in history]
    return "\n".join(lines)