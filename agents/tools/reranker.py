"""Reranker tool: precise (query, chunk) relevance scoring via a
cross-encoder model. Not a generative LLM -- a small scoring-only model
that looks at the query and chunk together, which is more accurate than
the similarity/BM25 scores used for the initial candidate pool.

Fails soft: if the model can't be loaded, reranking is skipped and
candidates are returned in their original order rather than crashing.
"""
import logging
from typing import Optional

from schemas.retriever_schema import Evidence

logger = logging.getLogger(__name__)

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    def __init__(self):
        self._model = None  # None = not yet tried, False = tried and failed

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(MODEL_NAME)
                logger.info("Loaded reranker model: %s", MODEL_NAME)
            except Exception as exc:
                logger.warning("Reranker model unavailable, skipping reranking: %s", exc)
                self._model = False
        return self._model or None

    def rerank(self, query: str, candidates: list[Evidence]) -> list[Evidence]:
        if not candidates:
            return []

        model = self._get_model()
        if model is None:
            return candidates  # degrade gracefully: keep original order

        try:
            pairs = [(query, candidate.content) for candidate in candidates]
            scores = model.predict(pairs)
        except Exception as exc:
            logger.warning("Reranking failed, returning original order: %s", exc)
            return candidates

        for candidate, score in zip(candidates, scores):
            candidate.score = float(score)

        return sorted(candidates, key=lambda c: c.score if c.score is not None else 0.0, reverse=True)
