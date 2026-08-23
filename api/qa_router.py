from fastapi import APIRouter

from schemas.Qa_schema import QARequest, QAResponse
from services.orchestrator import QAOrchestrator


router = APIRouter(
    prefix="/qa",
    tags=["QA"],
)

orchestrator = QAOrchestrator()


@router.post("/ask", response_model=QAResponse)
def ask_question(request: QARequest) -> QAResponse:

    result = orchestrator.run(request.question)

    return QAResponse(
        answer=result.answer,
        decision=result.decision,
        iterations=result.iterations,
        feedback=result.feedback,
    )