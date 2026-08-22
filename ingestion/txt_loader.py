"""Loader for plain .txt files.

Simplest source -> implemented first, used to validate the rest of the
pipeline (chunking -> embeddings -> vector store -> retrieval) end to end.
"""
import logging
import os
from typing import List

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def load_txt(file_path: str) -> List[Document]:
    """Read a .txt file and return it as a standardized Document list.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file is empty.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"TXT file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    if not text.strip():
        raise ValueError(f"TXT file is empty: {file_path}")

    logger.info("Loaded TXT file: %s (%d chars)", file_path, len(text))

    return [
        Document(
            page_content=text,
            metadata={"source": os.path.basename(file_path), "type": "txt"},
        )
    ]
