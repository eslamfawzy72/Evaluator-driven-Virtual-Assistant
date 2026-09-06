from pydantic import BaseModel

from schemas.retriever_schema import Evidence


class RetrieveMoreEvidenceInput(BaseModel):
    follow_up_query: str
    already_have: list[Evidence]