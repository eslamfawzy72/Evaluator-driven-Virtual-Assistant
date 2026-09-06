from agents.tools.retreive_more_tool import RetrieveMoreEvidenceTool
from schemas.retrieve_more_evidence_schema import RetrieveMoreEvidenceInput
from schemas.retriever_schema import Evidence


def main():
    already_have = [
        Evidence(
            content="BERT achieved 91% accuracy on the classification task.",
            source="paper_a.pdf",
            page_number=5,
        )
    ]

    input_data = RetrieveMoreEvidenceInput(
        follow_up_query="Find evidence about the methodology used in BERT.",
        already_have=already_have,
    )

    tool = RetrieveMoreEvidenceTool()

    results = tool.retrieve(input_data)

    print("\n========== NEW EVIDENCE ==========")

    for evidence in results:
        print(f"\nDocument: {evidence.source}")
        print(f"Content: {evidence.content}")

    print("\n==================================")


if __name__ == "__main__":
    main()