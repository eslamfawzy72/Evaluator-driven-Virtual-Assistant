from agents.tools.table_extractor import TableExtractor
from schemas.evidence_schema import Evidence


def main():
    evidences = [
    Evidence(
        id="ev_001",
        document_name="paper.pdf",
        page_number=5,
        content="Model Accuracy F1 Score",
    ),
    Evidence(
        id="ev_002",
        document_name="paper.pdf",
        page_number=5,
        content="""
        BERT 91.2% 90.4%
        RoBERTa 93.1% 92.5%
        """,
    ),
]

    extractor = TableExtractor()

    result = extractor.extract_table(evidences)

    print("Columns:")
    print(result.columns)

    print("\nRows:")
    for row in result.rows:
        print(row)


if __name__ == "__main__":
    main()