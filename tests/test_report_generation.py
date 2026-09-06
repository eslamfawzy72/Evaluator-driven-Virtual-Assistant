"""Verify the /report/generate endpoint produces a real, valid PDF."""
from fastapi.testclient import TestClient

from app import app
from ingestion.ingest import ingest

client = TestClient(app)


def test_generate_report_returns_pdf(tmp_path):
    content = "Report generation marker: obsidian-marmot-11209."
    file_path = tmp_path / "report_test.txt"
    file_path.write_text(content, encoding="utf-8")
    ingest(str(file_path), ".txt")

    response = client.post(
        "/report/generate",
        json={"question": "What is the report generation marker?"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    # A real PDF starts with this magic header
    assert response.content[:5] == b"%PDF-"
    assert len(response.content) > 500  # not an empty/broken PDF
