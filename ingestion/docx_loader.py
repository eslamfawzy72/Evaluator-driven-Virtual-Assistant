"""Loader for DOCX files.

Uses Docx2txtLoader (LangChain), same shape as pdf_loader.py.
"""
import logging
import os
from typing import List

from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def load_docx(file_path: str) -> List[Document]:
    """Extract text from a DOCX file and return standardized Documents.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if extraction fails or no extractable text is found.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"DOCX file not found: {file_path}")

    try:
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
    except Exception as exc:
        logger.error("Failed to extract DOCX %s: %s", file_path, exc)
        raise ValueError(f"Could not extract text from DOCX: {file_path}") from exc

    filename = os.path.basename(file_path)
    for doc in docs:
        doc.metadata["source"] = filename
        doc.metadata["type"] = "docx"

    docs = [d for d in docs if d.page_content.strip()]
    if not docs:
        raise ValueError(
            f"No extractable text found in DOCX (possibly empty): {file_path}"
        )

    logger.info("Loaded DOCX: %s (%d part(s) with text)", filename, len(docs))
    return docs