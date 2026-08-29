from schemas.retriever_schema import Evidence
from agents.analyzer_agent import AnalystAgent


def main():

    evidences = [
        Evidence(
            source="paper.pdf",
            page=5,
            content="""
    Model       Accuracy    F1
    BERT        91          89
    RoBERTa     94          92
    DistilBERT  89          87
    """
        )
    ]
    agent = AnalystAgent()

    result = agent.analyze(
        query="What is the difference between BERT and RoBERTa accuracy?",
        evidences=evidences,
    )


    print("\n========== ANALYST ==========")
    print(result)
    print("=============================")


if __name__ == "__main__":
    main()