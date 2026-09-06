import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.qa_router import orchestrator  # reuse the same instance -> shared Generator/Evaluator memory
from rag.retriever import retrieve
from schemas.report_schema import ReportRequest
from services.report_generator import generate_qa_report_pdf

router = APIRouter(prefix="/report", tags=["Report"])


@router.post("/generate")
def generate_report(request: ReportRequest):
    """Runs the full Q&A workflow for the question, then returns a PDF
    report of the question, final answer, validation status, and the
    source evidence used -- as a downloadable file, not JSON."""
    try:
        sources = retrieve(request.question)
        result = orchestrator.run(request.question)

        pdf_bytes = generate_qa_report_pdf(
            question=request.question,
            answer=result.answer,
            decision=result.decision,
            iterations=result.iterations,
            sources=sources,
            feedback=result.feedback,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}") from exc

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=qa_report.pdf"},
    )
