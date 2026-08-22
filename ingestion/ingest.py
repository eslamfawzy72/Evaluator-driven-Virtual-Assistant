
import logging

from ingestion.file_router import route
from rag.chunking import split_documents
from rag.vector_store import add_documents

logger = logging.getLogger(__name__)


def ingest(source: str, source_type: str = None) -> int:

    logger.info("Ingestion started: source=%s type=%s", source, source_type)

    documents = route(source, source_type)
    if not documents:
        raise ValueError(f"No content extracted from source: {source}")

    chunks = split_documents(documents)
    if not chunks:
        raise ValueError(f"Chunking produced no chunks for source: {source}")

    add_documents(chunks)

    logger.info(
        "Ingestion completed: source=%s documents=%d chunks=%d",
        source, len(documents), len(chunks),
    )
    return len(chunks)