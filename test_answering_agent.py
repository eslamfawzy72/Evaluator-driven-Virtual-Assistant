from agents.answering_agent import AnsweringAgent
from schemas.answering_input import AnsweringInput
from schemas.retriever_schema import Evidence


def main():

    agent = AnsweringAgent()

    evidences = [
        Evidence(
            source="paper.pdf",
            page=5,
            content="BERT achieved 91% accuracy."
        )
    ]

    input_data = AnsweringInput(
    query="What is the difference between BERT and RoBERTa accuracy?",
    evidences=[
        Evidence(
            id="evidence_1",
            source="paper_a.pdf",
            page=5,
            content="BERT achieved 91% accuracy."
        ),
        Evidence(
            id="evidence_2",
            source="paper_b.pdf",
            page=7,
            content="RoBERTa achieved 94% accuracy."
        )
    ],
    analysis=(
        "RoBERTa achieved 94% accuracy while BERT achieved 91%. "
        "The difference is 3 percentage points."
    )
)

    result = agent.answer(input_data)

    print("\n========== ANSWERING AGENT ==========")
    print(result)
    print("======================================")


if __name__ == "__main__":
    main()