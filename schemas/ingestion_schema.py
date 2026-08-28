from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    source: str = Field(..., min_length=1)
    source_type: str | None = None


class IngestionResponse(BaseModel):
    message: str
    source: str
    chunks_added: int