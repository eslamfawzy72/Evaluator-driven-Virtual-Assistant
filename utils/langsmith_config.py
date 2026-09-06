"""LangSmith tracing setup.

LangChain reads tracing config from environment variables directly (not
from any explicit API call) -- once LANGCHAIN_TRACING_V2=true and a valid
LANGCHAIN_API_KEY are set in os.environ, every LangChain chain/LLM call
(services/llm_service.py's ChatHuggingFace, rag/vector_store.py's Chroma
calls, etc.) is automatically traced to smith.langchain.com with no other
code changes needed.

Call configure_langsmith() once at app startup, before any LangChain code
runs. Safe to call with no API key configured -- tracing just stays off.
"""
import logging
import os

from config.settings import settings

logger = logging.getLogger(__name__)


def configure_langsmith() -> None:
    if not settings.langsmith_tracing:
        logger.info("LangSmith tracing disabled (LANGCHAIN_TRACING_V2 not set to true)")
        return

    if not settings.langsmith_api_key:
        logger.warning(
            "LANGCHAIN_TRACING_V2=true but LANGCHAIN_API_KEY is empty -- "
            "tracing will not actually send anything. Get a key at "
            "https://smith.langchain.com and set it in .env"
        )
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
    os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint

    logger.info("LangSmith tracing enabled for project '%s'", settings.langsmith_project)
