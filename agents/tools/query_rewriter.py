"""Query Rewriter tool: the only Retriever tool that calls an LLM.
Cleans up vague/pronoun-heavy follow-up questions using conversation
history before they're handed to search.

Fails soft: if the LLM service can't be constructed or the call fails,
the original query is returned unchanged rather than blocking retrieval.
"""
import logging
from typing import Optional

from agents.prompts.retriever_agent_prompt import QUERY_REWRITER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class QueryRewriter:
    def __init__(self, llm_service=None):
        # None = not yet tried, False = tried and failed, otherwise a real LLMService
        self._llm_service = llm_service if llm_service is not None else None
        self._attempted = llm_service is not None

    def _get_llm_service(self):
        if not self._attempted:
            self._attempted = True
            try:
                from services.llm_service import LLMService
                self._llm_service = LLMService()
            except Exception as exc:
                logger.warning("LLM service unavailable, query rewriting disabled: %s", exc)
                self._llm_service = None
        return self._llm_service

    def rewrite(self, query: str, conversation_history: Optional[list[str]] = None) -> str:
        llm_service = self._get_llm_service()
        if llm_service is None:
            return query

        history_str = "\n".join(conversation_history) if conversation_history else "None"
        user_message = (
            f"Conversation history:\n{history_str}\n\n"
            f"Latest question: {query}\n\n"
            f"Rewritten query:"
        )

        try:
            rewritten = llm_service.chat(QUERY_REWRITER_SYSTEM_PROMPT, user_message)
            rewritten = rewritten.strip()
            return rewritten or query
        except Exception as exc:
            logger.warning("Query rewrite failed, using original query %r: %s", query, exc)
            return query
