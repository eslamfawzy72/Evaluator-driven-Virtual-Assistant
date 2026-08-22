"""Loader for WAV audio files: speech-to-text -> normal ingestion pipeline.

Uses faster-whisper (local, no API key required) to transcribe. The model
is loaded once and cached, since loading it is the expensive part.
"""
import logging
import os
from typing import List

from faster_whisper import WhisperModel
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# "tiny"/"base" keep this fast for a project of this scope; swap to a
# larger model (e.g. "small"/"medium") if transcription accuracy matters
# more than speed.
MODEL_SIZE = "base"

_model = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        logger.info("Loading Whisper model: %s", MODEL_SIZE)
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def load_audio(file_path: str) -> List[Document]:
    """Transcribe a WAV file to text and return it as a standardized Document.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if transcription fails or produces no text.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"WAV file not found: {file_path}")

    try:
        model = _get_model()
        segments, _info = model.transcribe(file_path)
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as exc:
        logger.error("Transcription failed for %s: %s", file_path, exc)
        raise ValueError(f"Could not transcribe WAV file: {file_path}") from exc

    if not transcript:
        raise ValueError(f"Transcription produced no text (silent/unclear audio): {file_path}")

    filename = os.path.basename(file_path)
    logger.info("Transcribed WAV: %s (%d chars)", filename, len(transcript))

    return [
        Document(
            page_content=transcript,
            metadata={"source": filename, "type": "audio"},
        )
    ]
