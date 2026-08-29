from pydantic import BaseModel

from schemas.retriever_schema import Evidence


class AnalystInput(BaseModel):
    query: str
    evidences: list[Evidence]
    
class AnalystResult(BaseModel):
    analysis: str
    evidences: list[Evidence]