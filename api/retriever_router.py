from fastapi import APIRouter, HTTPException

from agents.retriever_agent import RetrieverAgent
from schemas.retriever_schema import RetrieverRequest, RetrieverResponse

router = APIRouter(prefix="/retriever", tags=["Retriever"])

# Built once, reused across requests -- KeywordSearch's BM25 index and the
# Reranker's cross-encoder model are both expensive to (re)build, so this
# mirrors qa_router.py's module-level orchestrator instance.
_agent = RetrieverAgent()


@router.post("/search", response_model=RetrieverResponse)
def search(request: RetrieverRequest) -> RetrieverResponse:
    try:
        evidence = _agent.retrieve(
            query=request.question,
            conversation_history=request.conversation_history,
            metadata_filter=request.metadata_filter,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}") from exc

    return RetrieverResponse(evidence=evidence, count=len(evidence))
