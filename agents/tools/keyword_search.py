"""Keyword Search tool: exact/lexical term matching via BM25.

Complements Semantic Search -- catches exact technical terms, IDs, and
names that an embedding-based search can sometimes miss.

The BM25 index is built lazily over the full corpus (rag/vector_store.py's
get_all_documents()) and rebuilt automatically whenever the knowledge base
changes, using the same knowledge-version counter the Redis cache relies
on -- so this never needs to be manually refreshed after an ingest.
"""
import logging
import re
from typing import Optional

from rank_bm25 import BM25Okapi

from cache.redis_cache import get_knowledge_version
from rag.vector_store import get_all_documents
from schemas.retriever_schema import Evidence

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


class KeywordSearch:
    def __init__(self):
        self._bm25: Optional[BM25Okapi] = None
        self._docs = []
        self._indexed_version = None

    def _ensure_index(self) -> None:
        current_version = get_knowledge_version()
        if self._bm25 is not None and self._indexed_version == current_version:
            return  # index is already up to date

        docs = get_all_documents()
        if not docs:
            self._bm25 = None
            self._docs = []
            self._indexed_version = current_version
            return

        tokenized_corpus = [_tokenize(doc.page_content) for doc in docs]
        self._bm25 = BM25Okapi(tokenized_corpus)
        self._docs = docs
        self._indexed_version = current_version
        logger.info("Built BM25 index over %d chunk(s) (knowledge_version=%s)", len(docs), current_version)

    def search(self, query: str, k: int = 20, filter: Optional[dict] = None) -> list[Evidence]:
        """`filter` is a flat {field: value} dict, applied by exact match
        against each chunk's metadata -- unlike semantic_search's `filter`,
        which is a Chroma `where` clause (see agents/tools/metadata_filter.py).
        """
        try:
            self._ensure_index()
        except Exception as exc:
            logger.error("Failed to build/refresh BM25 index: %s", exc)
            return []

        if self._bm25 is None:
            return []

        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(zip(self._docs, scores), key=lambda pair: pair[1], reverse=True)

        results = []
        for doc, score in ranked:
            if score <= 0:
                break  # BM25Okapi scores are sorted; no point scanning zero-score tail
            if filter and not all(doc.metadata.get(key) == value for key, value in filter.items()):
                continue
            results.append(
                Evidence(
                    content=doc.page_content,
                    source=doc.metadata.get("source", "unknown"),
                    page=doc.metadata.get("page"),
                    score=float(score),
                    metadata=doc.metadata,
                )
            )
            if len(results) >= k:
                break

        return results
