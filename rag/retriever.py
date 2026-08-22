"""Public retrieval interface -- the integration contract with Teammate 2.

    context = retrieve(question)

Returned shape (list of dicts, NOT LangChain Document objects) is what
Teammate 2's Generator/Evaluator consume directly:

    [{"content": "...", "source": "project.pdf"}]
"""
import logging
from typing import Dict, List

from cache.redis_cache import get_cached_retrieval, set_cached_retrieval
from rag.vector_store import similarity_search

logger = logging.getLogger(__name__)


def retrieve(question: str, k: int = 4) -> List[Dict[str, str]]:
    """Retrieve the top-k relevant chunks for a question.

    Checks Redis cache first; on miss, runs similarity search and caches
    the result. Returns an empty list (never raises) when nothing relevant
    is found or the vector store is empty -- callers (Teammate 2's
    workflow) are expected to handle "unknown question" on empty context.
    """
    if not question or not question.strip():
        logger.warning("retrieve() called with empty question")
        return []

    cached = get_cached_retrieval(question, k)
    if cached is not None:
        logger.info("Cache HIT for retrieval: %r", question)
        return cached

    logger.info("Cache MISS for retrieval: %r", question)
    try:
        docs = similarity_search(question, k=k)
    except Exception as exc:
        logger.error("Retrieval failed for question %r: %s", question, exc)
        return []

    context = [
        {"content": doc.page_content, "source": doc.metadata.get("source", "unknown")}
        for doc in docs
    ]

    set_cached_retrieval(question, k, context)
    return context
