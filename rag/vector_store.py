"""Chroma-backed vector store: persistence, storage, and similarity search."""
import logging
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from cache.redis_cache import bump_knowledge_version
from config.settings import settings
from rag.embeddings import get_embedding_function

logger = logging.getLogger(__name__)

# Sourced from config.settings (env-var overridable) so the test suite can
# point at an isolated, throwaway store instead of polluting (or being
# polluted by) the real persisted knowledge base across repeated test runs.
PERSIST_DIRECTORY = settings.chroma_persist_dir
COLLECTION_NAME = settings.chroma_collection_name

_vector_store = None


def get_vector_store() -> Chroma:
    """Return a cached, lazily-initialized Chroma vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embedding_function(),
            persist_directory=PERSIST_DIRECTORY,
        )
    return _vector_store


def add_documents(chunks: List[Document]) -> None:
    """Embed and persist a list of chunked Documents."""
    if not chunks:
        logger.warning("add_documents called with an empty chunk list; skipping")
        return
    store = get_vector_store()
    store.add_documents(chunks)
    logger.info("Stored %d chunk(s) in Chroma collection '%s'", len(chunks), COLLECTION_NAME)

    # The knowledge base just changed -- invalidate every retrieval/answer
    # cached under the previous version.
    bump_knowledge_version()


def similarity_search(
    question: str, k: int = 4, filter: Optional[dict] = None
) -> List[Document]:
    """Return the k most similar chunks to the question.

    `filter` maps directly to Chroma's `where` clause (e.g.
    {"source": "paper.pdf"} or {"$and": [...]} for multiple conditions) --
    used by the Retriever Agent's Metadata Filter tool.
    """
    store = get_vector_store()
    return store.similarity_search(question, k=k, filter=filter)


def get_all_documents() -> List[Document]:
    """Return every chunk currently stored, for tools that need the full
    corpus rather than a similarity search (e.g. building a BM25 index for
    keyword search)."""
    store = get_vector_store()
    raw = store.get(include=["documents", "metadatas"])
    return [
        Document(page_content=content, metadata=metadata or {})
        for content, metadata in zip(raw["documents"], raw["metadatas"])
    ]
