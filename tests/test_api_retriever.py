"""Verify the /retriever/search endpoint works end-to-end: ingest real
content, then confirm the API returns it as evidence."""
from fastapi.testclient import TestClient

from app import app
from ingestion.ingest import ingest

client = TestClient(app)


def test_retriever_search_endpoint_finds_ingested_content(tmp_path):
    content = "The retriever API endpoint marker: tungsten-falcon-30442."
    file_path = tmp_path / "retriever_api_test.txt"
    file_path.write_text(content, encoding="utf-8")

    ingest(str(file_path), ".txt")

    response = client.post(
        "/retriever/search",
        json={"question": "What is the retriever API endpoint marker?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["count"] > 0
    assert any("tungsten-falcon-30442" in e["content"] for e in body["evidence"])


def test_retriever_search_endpoint_rejects_empty_question():
    response = client.post("/retriever/search", json={"question": ""})
    assert response.status_code == 422  # pydantic min_length=1 validation
