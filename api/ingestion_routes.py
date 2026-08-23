"""FastAPI endpoints for the ingestion pipeline.

Thin wrappers around ingestion.ingest.ingest() -- all the actual loading /
chunking / embedding / storing logic stays in that one function. These
routes just handle the HTTP-specific concerns: file upload -> temp file,
request/response models, and mapping errors to status codes.
"""
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ingestion.ingest import ingest as ingest_source

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingestion"])


class IngestResponse(BaseModel):
    source: str
    chunks_stored: int


class URLIngestRequest(BaseModel):
    url: str


class WikipediaIngestRequest(BaseModel):
    topic: str


def _run_ingest(source: str, source_type: Optional[str]) -> int:
    """Call ingest() and translate its exceptions into HTTP errors.

    FileNotFoundError/ValueError are the "expected" failure modes raised
    by every loader (bad input, empty file, extraction failure, etc.) --
    those map to 400. Anything else is unexpected -> 500, without leaking
    internals beyond a logged message.
    """
    try:
        return ingest_source(source, source_type)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected ingestion failure for source=%s", source)
        raise HTTPException(status_code=500, detail="Ingestion failed unexpectedly") from exc


@router.post("/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    """Ingest an uploaded file (.txt, .pdf, .docx, code, .ppt/.pptx, .wav).

    Source and source_type are both detected automatically from the
    uploaded filename -- the caller only ever needs to provide the file.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    suffix = Path(file.filename).suffix.lower()
    if not suffix:
        raise HTTPException(
            status_code=400,
            detail=f"Could not detect file type: '{file.filename}' has no extension",
        )

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail=f"Uploaded file is empty: {file.filename}")
            tmp.write(contents)
            tmp_path = tmp.name

        num_chunks = _run_ingest(tmp_path, suffix)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return IngestResponse(source=file.filename, chunks_stored=num_chunks)


@router.post("/url", response_model=IngestResponse)
async def ingest_url(payload: URLIngestRequest):
    """Ingest a web page by URL."""
    num_chunks = _run_ingest(payload.url, "url")
    return IngestResponse(source=payload.url, chunks_stored=num_chunks)


@router.post("/wikipedia", response_model=IngestResponse)
async def ingest_wikipedia(payload: WikipediaIngestRequest):
    """Ingest a Wikipedia topic/page."""
    num_chunks = _run_ingest(payload.topic, "wikipedia")
    return IngestResponse(source=payload.topic, chunks_stored=num_chunks)
