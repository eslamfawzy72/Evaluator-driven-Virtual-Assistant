"""Verify the URL loader works end-to-end, and handles invalid/unreachable URLs."""
import pytest

from ingestion.ingest import ingest
from ingestion.url_loader import load_url
from rag.retriever import retrieve


def test_ingest_url_and_retrieve():
    # example.com: minimal, stable, static page reserved for testing use.
    url = "https://example.com"
    num_chunks = ingest(url, "url")
    assert num_chunks > 0

    context = retrieve("What is this domain used for?", k=2)
    assert len(context) > 0


def test_invalid_url_scheme_raises():
    with pytest.raises(ValueError):
        load_url("not-a-real-url")


def test_unreachable_url_raises():
    with pytest.raises(ValueError):
        load_url("https://this-domain-definitely-does-not-exist-123456.com")
