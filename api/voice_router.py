import logging
import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from api.qa_router import orchestrator
from ingestion.audio_loader import transcribe_audio
from schemas.voice_schema import VoiceQueryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post("/ask", response_model=VoiceQueryResponse)
async def ask_by_voice(file: UploadFile = File(...)):
    """Ask a question by voice: upload a WAV recording, it's transcribed,
    then run through the same Generator/Evaluator workflow as /qa/ask.

    This transcribes the SPOKEN QUESTION -- it does not add anything to
    the knowledge base. For adding spoken content as knowledge, use
    /ingest/file with a .wav file instead.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail=f"Uploaded file is empty: {file.filename}")
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            question = transcribe_audio(tmp_path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    try:
        result = orchestrator.run(question)
    except Exception as exc:
        logger.exception("Voice query workflow failed for transcribed question: %r", question)
        raise HTTPException(status_code=500, detail=f"Answering failed: {exc}") from exc

    return VoiceQueryResponse(
        transcribed_question=question,
        answer=result.answer,
        decision=result.decision,
        iterations=result.iterations,
        feedback=result.feedback,
    )
