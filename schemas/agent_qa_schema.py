from pydantic import BaseModel, Field

from schemas.retriever_schema import Evidence


class AgentQARequest(BaseModel):
    question: str = Field(..., min_length=1)


class AgentQAResponse(BaseModel):
    answer: str
    analysis: str
    evidence: list[Evidence]
    evidence_count: int
