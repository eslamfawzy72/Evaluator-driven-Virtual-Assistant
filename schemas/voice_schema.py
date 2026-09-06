from pydantic import BaseModel


class VoiceQueryResponse(BaseModel):
    transcribed_question: str
    answer: str
    decision: str
    iterations: int
    feedback: str | None = None
