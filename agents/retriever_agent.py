"""The Retriever Agent: finds relevant evidence in the vector database.

Never attempts to answer the question itself -- that's the Analyst and
Answer Agents' job. Runs a pipeline of 6 tools:

    query -> Query Rewriter (1 LLM call)
          -> Semantic Search + Keyword Search (run independently)
          -> merge/dedupe
          -> Reranker (cross-encoder, non-generative)
          -> Context Selector
          -> list[Evidence]

See agents/tools/ for each tool's implementation.
"""
import logging
from typing import Optional

from agents.tools.context_selector import select_context
from agents.tools.keyword_search import KeywordSearch
from agents.tools.metadata_filter import build_where_clause
from agents.tools.query_rewriter import QueryRewriter
from agents.tools.reranker import Reranker
from agents.tools.semantic_search import semantic_search
from schemas.retriever_schema import Evidence

logger = logging.getLogger(__name__)

DEFAULT_INITIAL_K = 20
DEFAULT_FINAL_K = 6


class RetrieverAgent:
    def __init__(
        self,
        llm_service=None,
        initial_k: int = DEFAULT_INITIAL_K,
        final_k: int = DEFAULT_FINAL_K,
    ):
        self.query_rewriter = QueryRewriter(llm_service)
        self.keyword_search = KeywordSearch()
        self.reranker = Reranker()
        self.initial_k = initial_k
        self.final_k = final_k

    def retrieve(
        self,
        query: str,
        conversation_history: Optional[list[str]] = None,
        metadata_filter: Optional[dict] = None,
    ) -> list[Evidence]:
        """Main entry point -- the Orchestrator calls this."""
        if not query or not query.strip():
            logger.warning("RetrieverAgent.retrieve() called with empty query")
            return []

        rewritten_query = self.query_rewriter.rewrite(query, conversation_history)
        if rewritten_query != query:
            logger.info("Query rewritten: %r -> %r", query, rewritten_query)

        semantic_hits = semantic_search(
            rewritten_query, k=self.initial_k, filter=build_where_clause(metadata_filter)
        )
        keyword_hits = self.keyword_search.search(
            rewritten_query, k=self.initial_k, filter=metadata_filter
        )

        candidates = self._merge_dedupe(semantic_hits, keyword_hits)
        if not candidates:
            logger.info("No candidates found for query: %r", rewritten_query)
            return []

        reranked = self.reranker.rerank(rewritten_query, candidates)
        return select_context(reranked, max_chunks=self.final_k)

    def retrieve_more(
        self,
        follow_up_query: str,
        already_have: list[Evidence],
        conversation_history: Optional[list[str]] = None,
        metadata_filter: Optional[dict] = None,
    ) -> list[Evidence]:
        """Called by the Analyst Agent's feedback loop when the initial
        evidence is insufficient. Same pipeline, but excludes chunks
        already retrieved so the Analyst gets genuinely new information."""
        new_evidence = self.retrieve(follow_up_query, conversation_history, metadata_filter)
        seen = {e.content.strip() for e in already_have}
        return [e for e in new_evidence if e.content.strip() not in seen]

    @staticmethod
    def _merge_dedupe(semantic_hits: list[Evidence], keyword_hits: list[Evidence]) -> list[Evidence]:
        """Combine both candidate lists, removing exact-content duplicates
        (a chunk can legitimately score high on both searches)."""
        merged: list[Evidence] = []
        seen_content: set[str] = set()
        for evidence in semantic_hits + keyword_hits:
            normalized = evidence.content.strip()
            if normalized and normalized not in seen_content:
                merged.append(evidence)
                seen_content.add(normalized)
        return merged
