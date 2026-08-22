"""Chroma-backed vector store: persistence, storage, and similarity search."""
import logging
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document

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


def similarity_search(question: str, k: int = 4) -> List[Document]:
    """Return the k most similar chunks to the question."""
    store = get_vector_store()
    return store.similarity_search(question, k=k)
