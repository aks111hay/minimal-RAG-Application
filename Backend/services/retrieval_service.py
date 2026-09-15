"""
Advanced retrieval pipeline:

  1. Dense retrieval  -> Chroma vector search (semantic similarity)
  2. Sparse retrieval -> BM25 keyword search (lexical overlap, catches
                          exact terms/names/codes embeddings can miss)
  3. Fusion           -> Reciprocal Rank Fusion (RRF) merges both ranked
                          lists without needing to normalize incomparable
                          similarity scores
  4. Re-ranking       -> a cross-encoder scores each fused candidate
                          against the query directly (far more accurate
                          than embedding cosine similarity, but too slow
                          to run over the whole corpus - hence step 3
                          narrows candidates first)

The cross-encoder model is loaded once at import time (lazy singleton)
since loading it is the slow part; the module-level `_cross_encoder`
cache keeps repeated queries fast.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

from backend.core.config import get_settings
from backend.models.schemas import RetrievedChunk
from backend.repositories import vector_store
from backend.utils.embeddings import get_embedding

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache
def _get_cross_encoder() -> CrossEncoder:
    logger.info("Loading cross-encoder model '%s' (first call only)", settings.cross_encoder_model)
    return CrossEncoder(settings.cross_encoder_model)


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


def _dense_search(query: str, top_k: int) -> list[tuple[str, str, dict, float]]:
    """Returns list of (id, document, metadata, distance)."""
    vector = get_embedding(query)
    result = vector_store.query_by_embedding(vector, top_k)

    ids = result.get("ids", [[]])[0]
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0] or [{}] * len(ids)
    dists = result.get("distances", [[]])[0] or [0.0] * len(ids)
    return list(zip(ids, docs, metas, dists))


def _sparse_search(query: str, top_k: int) -> list[tuple[str, str, dict]]:
    """BM25 over the full corpus currently stored in the vector DB."""
    corpus = vector_store.get_all_documents()
    ids = corpus.get("ids", [])
    docs = corpus.get("documents", [])
    metas = corpus.get("metadatas", []) or [{}] * len(ids)

    if not docs:
        return []

    tokenized_corpus = [_tokenize(d) for d in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(_tokenize(query))

    ranked = sorted(
        zip(ids, docs, metas, scores), key=lambda x: x[3], reverse=True
    )[:top_k]
    return [(i, d, m) for i, d, m, _ in ranked]


def _reciprocal_rank_fusion(
    dense_results: list[tuple[str, str, dict, float]],
    sparse_results: list[tuple[str, str, dict]],
    k: int,
) -> dict[str, dict]:
    """
    Merge two ranked lists into one score per document id using RRF:
    score(d) = sum(1 / (k + rank_i(d))) across each list it appears in.
    This avoids having to normalize cosine distance against BM25 score,
    which live on completely different scales.
    """
    fused: dict[str, dict] = {}

    for rank, (doc_id, text, meta, _dist) in enumerate(dense_results):
        entry = fused.setdefault(doc_id, {"text": text, "meta": meta, "score": 0.0})
        entry["score"] += 1.0 / (k + rank + 1)

    for rank, (doc_id, text, meta) in enumerate(sparse_results):
        entry = fused.setdefault(doc_id, {"text": text, "meta": meta, "score": 0.0})
        entry["score"] += 1.0 / (k + rank + 1)

    return fused


def _rerank(query: str, candidates: dict[str, dict], top_n: int) -> list[RetrievedChunk]:
    if not candidates:
        return []

    ids = list(candidates.keys())
    pairs = [(query, candidates[doc_id]["text"]) for doc_id in ids]

    cross_encoder = _get_cross_encoder()
    ce_scores = cross_encoder.predict(pairs)

    scored = sorted(zip(ids, ce_scores), key=lambda x: x[1], reverse=True)[:top_n]

    return [
        RetrievedChunk(
            id=doc_id,
            text=candidates[doc_id]["text"],
            source=candidates[doc_id]["meta"].get("source") if candidates[doc_id]["meta"] else None,
            score=float(score),
        )
        for doc_id, score in scored
    ]


def hybrid_retrieve(query: str, top_n: int | None = None) -> list[RetrievedChunk]:
    """
    Full pipeline: dense + sparse search -> RRF fusion -> cross-encoder rerank.
    Returns the top_n most relevant chunks, ready to feed into a prompt.
    """
    top_n = top_n or settings.rerank_top_n

    dense_results = _dense_search(query, settings.vector_top_k)
    sparse_results = _sparse_search(query, settings.bm25_top_k)

    logger.info(
        "Retrieved %d dense + %d sparse candidates for query", len(dense_results), len(sparse_results)
    )

    fused = _reciprocal_rank_fusion(dense_results, sparse_results, settings.rrf_k)
    reranked = _rerank(query, fused, top_n)

    logger.info("Reranked down to top %d chunks", len(reranked))
    return reranked
