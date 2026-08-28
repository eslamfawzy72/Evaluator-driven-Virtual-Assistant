from pydantic import BaseModel


class ExtractedTable(BaseModel):
    columns: list[str]
    rows: list[list[str]]