from fastapi import APIRouter, HTTPException

from agents.orchestrator import MultiAgentOrchestrator
from schemas.agent_qa_schema import AgentQARequest, AgentQAResponse

router = APIRouter(prefix="/agent", tags=["Agent"])

# Built once and reused across requests -- the Retriever's BM25 index and
# cross-encoder and the Analyst's tool bindings are all expensive to
# construct, so this mirrors qa_router.py's module-level orchestrator.
_orchestrator = MultiAgentOrchestrator()


@router.post("/ask", response_model=AgentQAResponse)
def ask_question(request: AgentQARequest) -> AgentQAResponse:
    try:
        result = _orchestrator.run(question=request.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AgentQAResponse(
        answer=result.answer,
        analysis=result.analysis,
        evidence=result.evidences,
        evidence_count=len(result.evidences),
    )
