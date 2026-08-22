"""Loader for source-code files.

Code is treated as plain external textual knowledge (like txt_loader) but
tags the detected language in metadata so retrieved chunks can show users
which file/language an answer came from.
"""
import logging
import os
from typing import List

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Maps file extension -> human-readable language name.
LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".java": "java",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
    ".rs": "rust",
    ".kt": "kotlin",
    ".swift": "swift",
    ".sql": "sql",
    ".sh": "shell",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
}


def load_code(file_path: str) -> List[Document]:
    """Read a source-code file and return it as a standardized Document list.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file is empty.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Code file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    if not text.strip():
        raise ValueError(f"Code file is empty: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    language = LANGUAGE_BY_EXTENSION.get(ext, "unknown")
    filename = os.path.basename(file_path)

    logger.info("Loaded code file: %s (language=%s, %d chars)", filename, language, len(text))

    return [
        Document(
            page_content=text,
            metadata={"source": filename, "type": "code", "language": language},
        )
    ]
