"""Verify /voice/ask: speech-to-question -> full Q&A workflow, end to end.

Generates a real speech WAV via Windows SAPI TTS (same technique as
tests/test_audio_ingestion.py), uploads it, and confirms the transcribed
question actually got answered.
"""
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from app import app
from ingestion.ingest import ingest

try:
    import win32com.client
    SAPI_AVAILABLE = True
except ImportError:
    SAPI_AVAILABLE = False

client = TestClient(app)


def _build_test_wav(path: str, text: str) -> None:
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    stream = win32com.client.Dispatch("SAPI.SpFileStream")
    stream.Open(path, 3, False)
    speaker.AudioOutputStream = stream
    speaker.Speak(text)
    stream.Close()


@pytest.mark.skipif(not SAPI_AVAILABLE, reason="Windows SAPI not available on this platform")
def test_voice_ask_transcribes_and_answers(tmp_path):
    content = "The voice query test marker is quantum-otter-64821."
    file_path = tmp_path / "voice_test.txt"
    file_path.write_text(content, encoding="utf-8")
    ingest(str(file_path), ".txt")

    wav_path = str(tmp_path / "question.wav")
    _build_test_wav(wav_path, "What is the voice query test marker?")

    with open(wav_path, "rb") as f:
        response = client.post(
            "/voice/ask",
            files={"file": ("question.wav", f, "audio/wav")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["transcribed_question"]
    assert "marker" in body["transcribed_question"].lower()
    assert body["answer"]


def test_voice_ask_rejects_empty_file():
    response = client.post(
        "/voice/ask",
        files={"file": ("empty.wav", b"", "audio/wav")},
    )
    assert response.status_code == 400
