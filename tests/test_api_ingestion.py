"""Verify the FastAPI ingestion endpoints work end-to-end."""
from fastapi.testclient import TestClient

from app import app
from rag.retriever import retrieve

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_file_endpoint_and_retrieve():
    content = b"FastAPI wraps the ingestion pipeline behind a simple HTTP interface."

    response = client.post(
        "/ingest/file",
        files={"file": ("api_test.txt", content, "text/plain")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "api_test.txt"
    assert body["chunks_stored"] > 0

    context = retrieve("What does FastAPI wrap?", k=2)
    assert len(context) > 0
    assert any("http interface" in c["content"].lower() for c in context)


def test_ingest_file_endpoint_rejects_empty_file():
    response = client.post(
        "/ingest/file",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 400


def test_ingest_url_endpoint_rejects_invalid_url():
    response = client.post("/ingest/url", json={"url": "not-a-real-url"})
    assert response.status_code == 400
