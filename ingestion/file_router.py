"""Detects source type and routes to the correct loader.

Only txt/pdf are wired up now (Priority 1). Add the remaining loaders
(docx, code, ppt, url, wikipedia, audio) here as they are implemented --
the rest of the pipeline never needs to know which branch fired.
"""
import os
from typing import List

from langchain_core.documents import Document

from ingestion.pdf_loader import load_pdf
from ingestion.txt_loader import load_txt
from ingestion.docx_loader import load_docx
from ingestion.code_loader import load_code, LANGUAGE_BY_EXTENSION
from ingestion.url_loader import load_url
from ingestion.wikipedia_loader import load_wikipedia
from ingestion.ppt_loader import load_ppt
from ingestion.audio_loader import load_audio

SUPPORTED_FILE_TYPES = {
    ".txt": load_txt,
    ".pdf": load_pdf,
    ".docx": load_docx,
    "url": load_url,
    "wikipedia": load_wikipedia,
    ".ppt": load_ppt,
    ".pptx": load_ppt,
    ".wav": load_audio,
}
# Every extension in LANGUAGE_BY_EXTENSION (.py, .js, .java, ...) routes to load_code.
SUPPORTED_FILE_TYPES.update({ext: load_code for ext in LANGUAGE_BY_EXTENSION})


def detect_source_type(source: str) -> str:
   
    if source.startswith("http://") or source.startswith("https://"):
        return "url"
    ext = os.path.splitext(source)[1].lower()
    if ext:
        return ext
    return "wikipedia"


def route(source: str, source_type: str = None) -> List[Document]:
   
    resolved_type = source_type or detect_source_type(source)

    if resolved_type in SUPPORTED_FILE_TYPES:
        return SUPPORTED_FILE_TYPES[resolved_type](source)

    raise ValueError(
        f"Unsupported source type '{resolved_type}' for source '{source}'. "
        f"Supported: {list(SUPPORTED_FILE_TYPES.keys())} (more coming: url, wikipedia, docx, ppt, code, wav)"
    )
