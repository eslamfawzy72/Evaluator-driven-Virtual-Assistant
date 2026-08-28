from fastapi import APIRouter, HTTPException

from schemas.ingestion_schema import IngestionRequest, IngestionResponse
from ingestion.ingest import ingest


router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"],
)


@router.post("/ingest", response_model=IngestionResponse)
def ingest_source(request: IngestionRequest):

    try:
        chunks_added = ingest(
            source=request.source,
            source_type=request.source_type,
        )

        return IngestionResponse(
            message="Ingestion completed successfully",
            source=request.source,
            chunks_added=chunks_added,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Ingestion failed",
        )