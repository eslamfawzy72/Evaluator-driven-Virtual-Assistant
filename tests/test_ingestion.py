"""Test 1 (from the spec): ingest a document and verify it can be retrieved."""
import os
import tempfile

from ingestion.ingest import ingest
from rag.retriever import retrieve


def test_ingest_txt_and_retrieve():
    content = "Redis is used as a caching layer to speed up repeated retrieval queries."
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        path = f.name

    try:
        num_chunks = ingest(path, ".txt")
        assert num_chunks > 0

        context = retrieve("What is Redis used for?", k=2)
        assert len(context) > 0
        assert any("caching" in c["content"].lower() for c in context)
    finally:
        os.remove(path)
