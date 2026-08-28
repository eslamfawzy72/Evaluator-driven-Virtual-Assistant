from pydantic import BaseModel, Field
from schemas.evidence_schema import Evidence

class AnalysisInput(BaseModel):
    question: str = Field(description="The user's original question")
    evidence: list[Evidence] = Field(
        description="Evidence retrieved from the user's documents"
    )