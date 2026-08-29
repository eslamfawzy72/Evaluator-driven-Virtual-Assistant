from pydantic import BaseModel, Field


class Evidence(BaseModel):
    id: str = Field(description="Unique identifier for this evidence item")
    document_name: str = Field(description="Name of the source document")
    page_number: int = Field(description="Page number where the evidence was found")
    content: str = Field(description="Relevant text extracted from the document")