"""
SQLite-backed conversation history store.

Chosen over pure in-memory storage so history survives server restarts
without requiring an external service like Redis - a good middle ground
for a portfolio project that should still "just run" with `uvicorn`.
"""

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages (session_id, id);
"""


@contextmanager
def _connect():
    conn = sqlite3.connect(settings.memory_db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(_SCHEMA)
    logger.info("Chat memory DB ready at %s", settings.memory_db_path)


def add_message(session_id: str, role: str, content: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.now(timezone.utc).isoformat()),
        )


def get_recent_messages(session_id: str, limit_turns: int) -> list[dict]:
    """
    Return the most recent `limit_turns` user/assistant pairs (i.e. up to
    2 * limit_turns rows), oldest-first, ready to feed into a prompt.
    """
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT role, content FROM messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit_turns * 2),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def clear_session(session_id: str) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    logger.info("Cleared chat history for session '%s'", session_id)