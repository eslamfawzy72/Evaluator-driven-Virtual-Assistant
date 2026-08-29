"""Shared data shape passed between the Retriever Agent's tools.

Richer than the old rag/retriever.py {"content", "source"} dict -- the
Analyst Agent needs page numbers for citations, and the reranker/context
selector need a score to reason about.
"""
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    content: str
    source: str
    page: int | None = None
    score: float | None = None
    metadata: dict = Field(default_factory=dict)


class RetrieverRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_history: list[str] | None = None
    metadata_filter: dict | None = None


class RetrieverResponse(BaseModel):
    evidence: list[Evidence]
    count: int
