"""
Recursive, structure-aware text chunking.

The original implementation sliced text every N raw characters, which
regularly cuts sentences (and words) in half and destroys semantic
coherence in a chunk. This version tries a cascade of separators from
"most meaningful" to "least meaningful" (paragraphs -> lines -> sentences
-> words -> characters), splitting on the first separator that actually
produces pieces small enough to fit within chunk_size. Overlap is then
applied by carrying trailing content forward into the next chunk so
retrieval doesn't lose context at chunk boundaries.

This mirrors the idea behind LangChain's RecursiveCharacterTextSplitter,
implemented directly so the mechanics are transparent (and dependency-free).
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Ordered from most- to least-semantically-meaningful split point.
_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]


def _split_on_separator(text: str, separator: str) -> list[str]:
    if separator == "":
        return list(text)
    if separator in (". ", "! ", "? "):
        # Keep the delimiter attached to the sentence it ends.
        pieces = re.split(f"(?<={re.escape(separator.strip())}) ", text)
        return [p for p in pieces if p]
    return [p for p in text.split(separator) if p != ""]


def _recursive_split(text: str, chunk_size: int, separators: list[str]) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    if not separators:
        # Fallback: hard character split.
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    sep, *rest = separators
    pieces = _split_on_separator(text, sep)

    # Merge small pieces back together up to chunk_size, splitting further
    # (with the next-level separator) any piece still too large.
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = (current + sep + piece) if current else piece
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(piece) > chunk_size:
                chunks.extend(_recursive_split(piece, chunk_size, rest))
                current = ""
            else:
                current = piece
    if current:
        chunks.append(current)

    return chunks


def split_text_into_chunks(
    text: str, chunk_size: int = 800, chunk_overlap: int = 150
) -> list[str]:
    """
    Split `text` into overlapping chunks, preferring paragraph/sentence
    boundaries over raw character cuts wherever possible.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    raw_chunks = _recursive_split(text, chunk_size, _SEPARATORS)

    if chunk_overlap == 0 or len(raw_chunks) <= 1:
        return raw_chunks

    # Apply overlap by prepending the tail of the previous chunk.
    overlapped: list[str] = [raw_chunks[0]]
    for chunk in raw_chunks[1:]:
        prev_tail = overlapped[-1][-chunk_overlap:]
        overlapped.append((prev_tail + chunk).strip())

    logger.debug("Split text of length %d into %d chunks", len(text), len(overlapped))
    return overlapped