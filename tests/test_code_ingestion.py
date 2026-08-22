"""Verify the source-code loader works end-to-end through ingest() -> retrieve()."""
import os
import tempfile

from ingestion.ingest import ingest
from rag.retriever import retrieve


def test_ingest_code_and_retrieve():
    content = (
        "def calculate_total_price(items):\n"
        "    # Sums the price field across a list of order items.\n"
        "    return sum(item['price'] for item in items)\n"
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        path = f.name

    try:
        num_chunks = ingest(path, ".py")
        assert num_chunks > 0

        context = retrieve("What does calculate_total_price do?", k=2)
        assert len(context) > 0
        assert any("price" in c["content"].lower() for c in context)
    finally:
        os.remove(path)
