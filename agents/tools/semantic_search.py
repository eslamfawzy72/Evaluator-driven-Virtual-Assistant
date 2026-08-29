
import logging
from typing import Optional

from rag.vector_store import similarity_search
from schemas.retriever_schema import Evidence

logger = logging.getLogger(__name__)


def semantic_search(query: str, k: int = 20, filter: Optional[dict] = None) -> list[Evidence]:
    """Return the k most semantically similar chunks to the query."""
    try:
        docs = similarity_search(query, k=k, filter=filter)
    except Exception as exc:
        logger.error("Semantic search failed for query %r: %s", query, exc)
        return []

    return [
        Evidence(
            content=doc.page_content,
            source=doc.metadata.get("source", "unknown"),
            page=doc.metadata.get("page"),
            metadata=doc.metadata,
        )
        for doc in docs
    ]
