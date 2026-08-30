from pydantic import BaseModel

from schemas.retriever_schema import Evidence


class AnsweringInput(BaseModel):

    query: str

    evidences: list[Evidence]

    analysis: str