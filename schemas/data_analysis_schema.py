from pydantic import BaseModel

from schemas.retriever_schema import Evidence
from schemas.table_extractor_schema import ExtractedTable
from schemas.comparison_schema import DocumentComparison


class DataAnalysisInput(BaseModel):
    query: str
    evidences: list[Evidence]
    extracted_table: ExtractedTable | None = None
    document_comparison: DocumentComparison | None = None
    
from pydantic import BaseModel


class DataAnalysisResult(BaseModel):
    calculations: list[str]
    trends: list[str]
    patterns: list[str]
    insights: list[str]