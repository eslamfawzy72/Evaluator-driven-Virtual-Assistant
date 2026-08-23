from pydantic import BaseModel, Field


class QARequest(BaseModel):
    question: str = Field(..., min_length=1)


class QAResponse(BaseModel):
    answer: str
    decision: str
    iterations: int
    feedback: str | None = None