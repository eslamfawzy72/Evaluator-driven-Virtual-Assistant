from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    question: str = Field(..., min_length=1)
