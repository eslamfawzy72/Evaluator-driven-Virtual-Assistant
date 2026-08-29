from schemas.retriever_schema import Evidence
from agents.analyzer_agent import AnalystAgent


def main():

    evidences = [
        Evidence(
            source="paper_a.pdf",
            page=5,
            content="BERT achieved 91% accuracy on the dataset."
        ),
        Evidence(
            source="paper_b.pdf",
            page=7,
            content="RoBERTa achieved 94% accuracy on the dataset."
        ),
    ]

    agent = AnalystAgent()

    result = agent.analyze(
        query="Use the Document Comparison tool to compare the evidence from paper_a.pdf and paper_b.pdf",
        evidences=evidences,
    )

    print("\n========== ANALYST ==========")
    print(result)
    print("=============================")


if __name__ == "__main__":
    main()