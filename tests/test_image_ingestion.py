"""Verify the image OCR loader works end-to-end: render text into an
image, ingest it, and confirm it's retrievable."""
import os

from PIL import Image, ImageDraw

from ingestion.ingest import ingest
from rag.retriever import retrieve


def _build_test_image(path: str, text: str) -> None:
    img = Image.new("RGB", (600, 150), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 50), text, fill="black")
    img.save(path)


def test_ingest_image_and_retrieve(tmp_path):
    text = "OCR ingestion marker CACTUS9284"
    image_path = str(tmp_path / "ocr_test.png")
    _build_test_image(image_path, text)

    num_chunks = ingest(image_path, ".png")
    assert num_chunks > 0

    context = retrieve("What is the OCR ingestion marker?", k=3)
    assert len(context) > 0
    assert any("cactus9284" in c["content"].lower() for c in context)
