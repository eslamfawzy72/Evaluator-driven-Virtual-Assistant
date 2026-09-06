from schemas.retriever_schema import Evidence
from agents.analyzer_agent import AnalystAgent
from schemas.table_extractor_schema import ExtractedTable


def main():

    evidences = [
        Evidence(
            source="paper.pdf",
            page=5,
            content="The model achieved strong performance on the dataset."
        )
    ]


    agent = AnalystAgent()

    result = agent.analyze(
        query="What exact accuracy did the model achieve?",
        evidences=evidences,
    )

    print("\n========== ANALYST ==========")
    print(result)
    print("=============================")


if __name__ == "__main__":
    main()