from pydantic import BaseModel


class DocumentAnalysis(BaseModel):
    document_name: str
    methodology: str | None
    results: str | None
    advantages: list[str]
    disadvantages: list[str]
    conclusions: str | None


class DocumentComparison(BaseModel):
    documents: list[DocumentAnalysis]
    similarities: list[str]
    differences: list[str]