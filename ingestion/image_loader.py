"""Loader for images (.png, .jpg, .jpeg, etc.): OCR -> normal ingestion
pipeline. Extracted text from a scanned page, screenshot, photo of a
whiteboard, etc. becomes searchable knowledge like any other source.

Uses EasyOCR (pure Python, no external Tesseract binary required -- just
pip-installable, works the same on Windows/Linux/Docker). The reader is
loaded once and cached, since loading it is the expensive part.
"""
import logging
import os
from typing import List

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

MIN_CONFIDENCE = 0.4  # drop very low-confidence OCR guesses (noise, artifacts)

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        logger.info("Loading EasyOCR reader (English)")
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def load_image(file_path: str) -> List[Document]:
    """Extract text from an image via OCR and return a standardized Document.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if OCR fails or produces no text above the confidence threshold.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    try:
        reader = _get_reader()
        results = reader.readtext(file_path)
    except Exception as exc:
        logger.error("OCR failed for %s: %s", file_path, exc)
        raise ValueError(f"Could not extract text from image: {file_path}") from exc

    lines = [text.strip() for _bbox, text, confidence in results if confidence >= MIN_CONFIDENCE and text.strip()]
    extracted_text = "\n".join(lines)

    if not extracted_text:
        raise ValueError(f"No text found in image (blank/non-text image, or OCR confidence too low): {file_path}")

    filename = os.path.basename(file_path)
    logger.info("OCR'd image: %s (%d line(s), %d chars)", filename, len(lines), len(extracted_text))

    return [
        Document(
            page_content=extracted_text,
            metadata={"source": filename, "type": "image"},
        )
    ]
