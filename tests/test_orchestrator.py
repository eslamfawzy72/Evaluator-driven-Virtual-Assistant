from services.orchestrator import QAOrchestrator


def main():
    orchestrator = QAOrchestrator()

    question = "What is natural language processing?"

    print("\n" + "=" * 60)
    print("FIRST REQUEST")
    print("=" * 60)

    result = orchestrator.run(question)

    print(f"Answer: {result.answer}")
    print(f"Decision: {result.decision}")
    print(f"Iterations: {result.iterations}")
    print(f"Feedback: {result.feedback}")

    print("\n" + "=" * 60)
    print("SECOND REQUEST")
    print("=" * 60)

    result = orchestrator.run(question)

    print(f"Answer: {result.answer}")
    print(f"Decision: {result.decision}")
    print(f"Iterations: {result.iterations}")
    print(f"Feedback: {result.feedback}")


if __name__ == "__main__":
    main()