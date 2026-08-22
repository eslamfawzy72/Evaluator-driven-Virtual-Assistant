"""Loader for Wikipedia topics/pages.

Uses WikipediaLoader (LangChain, backed by the `wikipedia` package) to
retrieve article content for a given topic or page title.
"""
import logging
from typing import List

import wikipedia
from langchain_community.document_loaders import WikipediaLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# How many candidate pages to fetch for a topic. Wikipedia topics are often
# ambiguous ("Mercury" -> planet/element/god/...); this doesn't disambiguate
# for the user, it just gives the retriever a couple of candidates to search.
MAX_RESULTS = 2

# Wikipedia's API now rejects unidentified clients with a 403 (see
# https://phabricator.wikimedia.org/T400119). The underlying `wikipedia`
# package sends no User-Agent by default, so this must be set globally
# before any lookup, or every request fails with a JSONDecodeError that
# masks the real 403 cause.
wikipedia.set_user_agent(
    "EvaluatorGeneratorRAG/1.0 (educational project; contact: mohamedwael3346@gmail.com)"
)


def load_wikipedia(topic: str) -> List[Document]:
    """Fetch Wikipedia article content for a topic and return standardized Documents.

    Raises:
        ValueError: if the topic is empty, the lookup fails, or no page is found.
    """
    if not topic or not topic.strip():
        raise ValueError("Wikipedia topic must not be empty")

    try:
        loader = WikipediaLoader(query=topic, load_max_docs=MAX_RESULTS)
        docs = loader.load()
    except Exception as exc:
        logger.error("Wikipedia lookup failed for topic %r: %s", topic, exc)
        raise ValueError(f"Could not retrieve Wikipedia page for topic: {topic}") from exc

    for doc in docs:
        # WikipediaLoader already sets metadata["title"]/["source"] (article URL);
        # keep both but make "source" the human-readable title for display.
        doc.metadata["source"] = doc.metadata.get("title", topic)
        doc.metadata["type"] = "wikipedia"

    docs = [d for d in docs if d.page_content.strip()]
    if not docs:
        raise ValueError(f"No Wikipedia page found for topic: {topic}")

    logger.info("Loaded Wikipedia topic: %r (%d page(s))", topic, len(docs))
    return docs
