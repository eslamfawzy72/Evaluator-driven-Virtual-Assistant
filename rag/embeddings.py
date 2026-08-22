
import logging

from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_embedding_function = None


def get_embedding_function():
    """Return a cached, lazily-initialized embedding function instance."""
    global _embedding_function
    if _embedding_function is None:
        logger.info("Loading embedding model: %s", DEFAULT_MODEL_NAME)
        _embedding_function = HuggingFaceEmbeddings(model_name=DEFAULT_MODEL_NAME)
    return _embedding_function
