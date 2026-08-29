"""End-to-end test for the Retriever Agent: ingest real content, then
verify retrieve() finds it via the full pipeline (query rewrite ->
semantic + keyword search -> merge -> rerank -> context selection)."""
import os
import tempfile

from agents.retriever_agent import RetrieverAgent
from ingestion.ingest import ingest


def test_retrieve_finds_ingested_content():
    content = (
        "The Retriever Agent uses BM25 for keyword search and a "
        "cross-encoder for reranking candidate chunks."
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        path = f.name

    try:
        ingest(path, ".txt")

        agent = RetrieverAgent()
        results = agent.retrieve("What does the Retriever Agent use for keyword search?")

        assert len(results) > 0
        assert any("bm25" in r.content.lower() for r in results)
        assert all(r.source for r in results)
    finally:
        os.remove(path)


def test_retrieve_empty_query_returns_empty_list():
    agent = RetrieverAgent()
    assert agent.retrieve("") == []
    assert agent.retrieve("   ") == []


def test_retrieve_more_excludes_already_seen_evidence():
    content = "Exclusive marker for retrieve_more test: zebra-quokka-77123."
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        path = f.name

    try:
        ingest(path, ".txt")

        agent = RetrieverAgent()
        first_pass = agent.retrieve("What is the exclusive marker?")
        assert len(first_pass) > 0

        follow_up = agent.retrieve_more("What is the exclusive marker?", already_have=first_pass)
        seen_contents = {e.content.strip() for e in first_pass}
        assert all(e.content.strip() not in seen_contents for e in follow_up)
    finally:
        os.remove(path)
