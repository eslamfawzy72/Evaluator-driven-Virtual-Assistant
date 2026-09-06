from agents.tools.docs_comparison_tool import DocumentComparisonTool
from schemas.evidence_schema import Evidence


def main():

    evidences = [
        Evidence(
            id="ev_001",
            document_name="paper_a.pdf",
            page_number=3,
            content="""
            BERT was fine-tuned on Dataset X.
            The model achieved 91% accuracy.
            Training required 2 hours.
            """,
        ),
        Evidence(
            id="ev_002",
            document_name="paper_a.pdf",
            page_number=4,
            content="""
            The authors concluded that BERT performed well
            on the classification task.
            """,
        ),
        Evidence(
            id="ev_003",
            document_name="paper_b.pdf",
            page_number=5,
            content="""
            RoBERTa was fine-tuned on Dataset X.
            The model achieved 94% accuracy.
            Training required 3 hours.
            """,
        ),
        Evidence(
            id="ev_004",
            document_name="paper_b.pdf",
            page_number=6,
            content="""
            The authors concluded that RoBERTa provided
            improved classification performance.
            """,
        ),
    ]

    tool = DocumentComparisonTool()

    result = tool.compare_documents(evidences)

    print("\n========== DOCUMENT COMPARISON ==========")
    print(result.model_dump_json(indent=2))
    print("==========================================")


if __name__ == "__main__":
    main()