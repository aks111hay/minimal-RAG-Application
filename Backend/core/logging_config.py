"""
Structured logging setup for the app.

Call configure_logging() once at startup (done in main.py). Every module
then just does `logger = logging.getLogger(__name__)` and logs normally;
formatting, level, and stream handling are centralized here.
"""

import logging
import sys

from backend.core.config import get_settings

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


def configure_logging() -> None:
    settings = get_settings()

    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())

    # Avoid duplicate handlers on reload (uvicorn --reload re-imports modules)
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))
    root.addHandler(handler)

    # Quiet down noisy third-party loggers unless we're in DEBUG mode
    if settings.log_level.upper() != "DEBUG":
        for noisy in ("httpx", "chromadb", "sentence_transformers", "urllib3"):
            logging.getLogger(noisy).setLevel(logging.WARNING)