"""Redis caching helpers for retrieval results.

Fails soft: if Redis is unreachable, every get_* returns None (cache miss)
and every set_* is a no-op with a logged warning -- the app must keep
working without caching, per the Shared Task 3 error-handling requirement.
"""
import hashlib
import json
import logging
from typing import List, Optional

import redis

from config.settings import settings

logger = logging.getLogger(__name__)

RETRIEVAL_TTL_SECONDS = 60 * 60  # 1 hour

_client = None


def get_client() -> Optional["redis.Redis"]:
    """Return a cached Redis client, or None if Redis is unavailable."""
    global _client
    if _client is None:
        try:
            _client = redis.Redis(
                host=settings.redis_host, port=settings.redis_port, db=settings.redis_db,
                decode_responses=True, socket_connect_timeout=2,
            )
            _client.ping()
        except Exception as exc:
            logger.warning("Redis unavailable, caching disabled: %s", exc)
            _client = False  # sentinel: "already tried, don't retry every call"
    return _client or None


KNOWLEDGE_VERSION_KEY = "knowledge_version"


def get_knowledge_version() -> str:
    """Current knowledge-base version tag.

    Every cache key that depends on the ingested knowledge (retrieval
    results, final answers) folds this in. Bumping it via
    bump_knowledge_version() -- called whenever new content is ingested --
    makes every previously-cached entry unreachable under the new version,
    which is a cheap way to invalidate a whole cache generation at once
    without tracking or deleting individual keys.

    Fails soft to a stable default ("v0") if Redis is unavailable --
    caching still works within a single process run, it just won't
    auto-invalidate across ingestion events without Redis.
    """
    client = get_client()
    if client is None:
        return "v0"
    try:
        version = client.get(KNOWLEDGE_VERSION_KEY)
        return version or "v0"
    except Exception as exc:
        logger.warning("Redis GET knowledge_version failed: %s", exc)
        return "v0"


def bump_knowledge_version() -> None:
    """Call after successfully ingesting new content."""
    client = get_client()
    if client is None:
        return
    try:
        client.incr(KNOWLEDGE_VERSION_KEY)
    except Exception as exc:
        logger.warning("Redis INCR knowledge_version failed: %s", exc)


def _retrieval_key(question: str, k: int, knowledge_version: str) -> str:
    digest = hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()
    return f"retrieval:{knowledge_version}:{digest}:k{k}"


def get_cached_retrieval(question: str, k: int, knowledge_version: str) -> Optional[List[dict]]:
    client = get_client()
    if client is None:
        return None
    try:
        raw = client.get(_retrieval_key(question, k, knowledge_version))
        return json.loads(raw) if raw else None
    except Exception as exc:
        logger.warning("Redis GET failed: %s", exc)
        return None


def set_cached_retrieval(question: str, k: int, knowledge_version: str, context: List[dict]) -> None:
    client = get_client()
    if client is None:
        return
    try:
        client.set(
            _retrieval_key(question, k, knowledge_version),
            json.dumps(context),
            ex=RETRIEVAL_TTL_SECONDS,
        )
    except Exception as exc:
        logger.warning("Redis SET failed: %s", exc)
        
QA_TTL_SECONDS = 60 * 60  # 1 hour


def _qa_key(question: str, knowledge_version: str) -> str:
    digest = hashlib.sha256(
        question.strip().lower().encode("utf-8")
    ).hexdigest()

    return f"qa:{knowledge_version}:{digest}"


def get_cached_answer(question: str, knowledge_version: str) -> Optional[dict]:
    client = get_client()

    if client is None:
        return None

    try:
        raw = client.get(_qa_key(question, knowledge_version))
        return json.loads(raw) if raw else None

    except Exception as exc:
        logger.warning("Redis QA GET failed: %s", exc)
        return None


def set_cached_answer(question: str, knowledge_version: str, result: dict) -> None:
    client = get_client()

    if client is None:
        return

    try:
        client.set(
            _qa_key(question, knowledge_version),
            json.dumps(result),
            ex=QA_TTL_SECONDS,
        )

    except Exception as exc:
        logger.warning("Redis QA SET failed: %s", exc)
