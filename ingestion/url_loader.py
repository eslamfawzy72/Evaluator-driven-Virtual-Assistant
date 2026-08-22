"""Loader for web pages via URL.

Uses WebBaseLoader (LangChain, backed by requests + BeautifulSoup) to fetch
and extract textual content from a page.
"""
import logging
from typing import List

import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_SECONDS = 10


def load_url(url: str) -> List[Document]:
    """Fetch a web page and return standardized Documents.

    Raises:
        ValueError: if the URL is malformed, unreachable, returns an error
            status, or yields no extractable text.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        raise ValueError(f"Invalid URL (missing http/https scheme): {url}")

    # Fail fast with a clear error before handing off to WebBaseLoader,
    # which otherwise raises a less obvious low-level exception.
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error("URL unreachable or invalid: %s (%s)", url, exc)
        raise ValueError(f"Could not reach URL: {url} ({exc})") from exc

    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
    except Exception as exc:
        logger.error("Failed to extract content from URL %s: %s", url, exc)
        raise ValueError(f"Could not extract content from URL: {url}") from exc

    for doc in docs:
        doc.metadata["source"] = url
        doc.metadata["type"] = "url"

    docs = [d for d in docs if d.page_content.strip()]
    if not docs:
        raise ValueError(f"No extractable text found at URL: {url}")

    logger.info("Loaded URL: %s (%d document(s))", url, len(docs))
    return docs
