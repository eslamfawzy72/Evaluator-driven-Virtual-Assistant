"""Loader for PDF files.

Uses PyPDFLoader (LangChain) which already returns one Document per page
with page metadata preserved.
"""
import logging
import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> List[Document]:
   
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    except Exception as exc:  # malformed PDF, encrypted, etc.
        logger.error("Failed to extract PDF %s: %s", file_path, exc)
        raise ValueError(f"Could not extract text from PDF: {file_path}") from exc

    filename = os.path.basename(file_path)
    for doc in docs:
        doc.metadata["source"] = filename
        doc.metadata["type"] = "pdf"
        # PyPDFLoader already sets metadata["page"]

    docs = [d for d in docs if d.page_content.strip()]
    if not docs:
        raise ValueError(
            f"No extractable text found in PDF (possibly scanned/image-only): {file_path}"
        )

    logger.info("Loaded PDF: %s (%d pages with text)", filename, len(docs))
    return docs
