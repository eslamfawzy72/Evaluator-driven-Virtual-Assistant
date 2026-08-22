from services.orchestrator import QAOrchestrator


def main():
    orchestrator = QAOrchestrator()

    question = "What is Natural Language Processing?"

    result = orchestrator.run(question)

    print("\n=== ORCHESTRATOR RESULT ===")

    print(f"Decision: {result.decision}")
    print(f"Iterations: {result.iterations}")

    print("\n=== FINAL ANSWER ===")
    print(result.answer)

    print("\n=== LAST EVALUATOR FEEDBACK ===")
    print(result.feedback)

    print("\n=== GENERATOR ATTEMPTS ===")

    for attempt in orchestrator.generator.memory.get_attempts():
        print(f"\nIteration: {attempt.iteration}")
        print(f"Answer: {attempt.answer}")

    print("\n=== EVALUATOR HISTORY ===")

    for evaluation in orchestrator.evaluator.memory.get_evaluations():
        print(f"\nIteration: {evaluation.iteration}")
        print(f"Decision: {evaluation.decision}")
        print(f"Feedback: {evaluation.feedback}")


if __name__ == "__main__":
    main()