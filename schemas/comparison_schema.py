from pydantic import BaseModel, Field


class DocumentAnalysis(BaseModel):
    document_name: str
    methodology: str | None
    results: str | None
    advantages: list[str] = Field(default_factory=list)
    disadvantages: list[str] = Field(default_factory=list)
    conclusions: str | None


class DocumentComparison(BaseModel):
    documents: list[DocumentAnalysis]
    similarities: list[str]
    differences: list[str]