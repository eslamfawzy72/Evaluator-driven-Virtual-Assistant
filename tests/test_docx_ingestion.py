"""Verify the DOCX loader works end-to-end through ingest() -> retrieve()."""
import os
import tempfile

import docx

from ingestion.ingest import ingest
from rag.retriever import retrieve


def test_ingest_docx_and_retrieve():
    content = "Chroma is used as the vector database to store document embeddings."

    doc = docx.Document()
    doc.add_paragraph(content)

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        path = f.name
    doc.save(path)

    try:
        num_chunks = ingest(path, ".docx")
        assert num_chunks > 0

        context = retrieve("What is Chroma used for?", k=2)
        assert len(context) > 0
        assert any("vector database" in c["content"].lower() for c in context)
    finally:
        os.remove(path)
