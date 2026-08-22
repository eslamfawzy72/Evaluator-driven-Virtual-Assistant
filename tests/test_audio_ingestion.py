"""Verify the WAV loader works end-to-end through ingest() -> retrieve().

Generates a real speech WAV file at test time using Windows SAPI
text-to-speech (offline, no extra dependency), transcribes it with
faster-whisper, and confirms the transcript is retrievable.
"""
import os
import tempfile

import pytest

try:
    import win32com.client
    SAPI_AVAILABLE = True
except ImportError:
    SAPI_AVAILABLE = False

from ingestion.ingest import ingest
from rag.retriever import retrieve


def _build_test_wav(path: str, text: str) -> None:
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    stream = win32com.client.Dispatch("SAPI.SpFileStream")
    stream.Open(path, 3, False)  # 3 = SSFMCreateForWrite
    speaker.AudioOutputStream = stream
    speaker.Speak(text)
    stream.Close()


@pytest.mark.skipif(not SAPI_AVAILABLE, reason="Windows SAPI not available on this platform")
def test_ingest_wav_and_retrieve():
    text = "Redis caching avoids repeating the same expensive vector search twice."

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    _build_test_wav(path, text)

    try:
        num_chunks = ingest(path, ".wav")
        assert num_chunks > 0

        context = retrieve("What does Redis caching avoid?", k=2)
        assert len(context) > 0
        assert any("vector search" in c["content"].lower() for c in context)
    finally:
        os.remove(path)
