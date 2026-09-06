"""Generates a PDF report for a single question + its final answer,
including the source evidence used, via reportlab.
"""
import io
import logging
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)


def generate_qa_report_pdf(
    question: str,
    answer: str,
    decision: str,
    iterations: int,
    sources: Optional[list[dict]] = None,
    feedback: Optional[str] = None,
) -> bytes:
    """Build a PDF report for one Q&A result. Returns the PDF as bytes
    (in-memory, no file written to disk) so callers can stream it straight
    back over HTTP.

    `sources` is a list of {"content": str, "source": str} dicts, the same
    shape rag/retriever.py::retrieve() and Evidence both use.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], fontSize=18, spaceAfter=6)
    heading_style = ParagraphStyle("SectionHeading", parent=styles["Heading2"], spaceBefore=16, spaceAfter=6)
    body_style = ParagraphStyle("Body", parent=styles["BodyText"], spaceAfter=8, leading=15)
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], textColor=colors.grey, fontSize=9)

    elements = []
    elements.append(Paragraph("Question &amp; Answer Report", title_style))
    elements.append(
        Paragraph(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style)
    )
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Question", heading_style))
    elements.append(Paragraph(_escape(question), body_style))

    elements.append(Paragraph("Answer", heading_style))
    elements.append(Paragraph(_escape(answer), body_style))

    status_table_data = [
        ["Validation status", decision.upper()],
        ["Iterations", str(iterations)],
    ]
    if feedback:
        status_table_data.append(["Evaluator feedback", feedback])

    status_table = Table(status_table_data, colWidths=[1.8 * inch, 4.2 * inch])
    status_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )
    elements.append(Spacer(1, 8))
    elements.append(status_table)

    if sources:
        elements.append(Paragraph("Sources", heading_style))
        for i, item in enumerate(sources, start=1):
            elements.append(
                Paragraph(f"<b>[{i}] {_escape(item.get('source', 'unknown'))}</b>", body_style)
            )
            elements.append(Paragraph(_escape(item.get("content", "")), body_style))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info("Generated Q&A report PDF (%d bytes) for question: %r", len(pdf_bytes), question)
    return pdf_bytes


def _escape(text: str) -> str:
    """reportlab's Paragraph interprets a small subset of HTML -- escape
    raw content so text like "a < b" doesn't break PDF layout."""
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
