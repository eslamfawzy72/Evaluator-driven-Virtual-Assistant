"""Main FastAPI application entry point.

Run with:
    uvicorn app:app --reload

Interactive docs at http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI

from api.ingestion_routes import router as ingestion_router
from api.qa_router import router as qa_router
from api.retriever_router import router as retriever_router
from utils.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="Evaluator-Generator AI Knowledge Platform",
    description="Ingestion + retrieval API for the Evaluator-Generator RAG workflow.",
)

app.include_router(ingestion_router)
app.include_router(qa_router)
app.include_router(retriever_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
