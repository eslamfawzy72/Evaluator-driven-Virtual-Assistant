"""Verify the Wikipedia loader works end-to-end, and handles missing pages."""
import pytest

from ingestion.ingest import ingest
from ingestion.wikipedia_loader import load_wikipedia
from rag.retriever import retrieve


def test_ingest_wikipedia_and_retrieve():
    num_chunks = ingest("Python (programming language)", "wikipedia")
    assert num_chunks > 0

    context = retrieve("Who created the Python programming language?", k=3)
    assert len(context) > 0


def test_wikipedia_empty_topic_raises():
    with pytest.raises(ValueError):
        load_wikipedia("")


def test_wikipedia_nonexistent_topic_raises():
    with pytest.raises(ValueError):
        load_wikipedia("asdkjqwoieuqwoeiuasdkjqwoieuasdqwe_definitely_not_a_real_page_xyz123")
