from services.evaluator_memory import EvaluatorMemory


def main():
    memory = EvaluatorMemory()

    context = [
        {
            "content": "NLP is a branch of artificial intelligence.",
            "source": "intro_to_nlp.pdf",
        }
    ]

    # Evaluation 1 - rejected
    memory.add_evaluation(
        question="What is NLP?",
        context=context,
        answer="NLP is a programming language.",
        decision="reject",
        feedback="The answer incorrectly describes NLP as a programming language.",
        accuracy=0.2,
        relevance=0.8,
        completeness=0.5,
        grounding=0.2,
    )

    # Evaluation 2 - accepted
    memory.add_evaluation(
        question="What is NLP?",
        context=context,
        answer="NLP is a branch of artificial intelligence.",
        decision="accept",
        feedback="The answer is accurate and supported by the provided context.",
        accuracy=1.0,
        relevance=1.0,
        completeness=1.0,
        grounding=1.0,
    )

    print("\n=== ALL EVALUATIONS ===")

    for evaluation in memory.get_evaluations():
        print(f"\nIteration: {evaluation.iteration}")
        print(f"Decision: {evaluation.decision}")
        print(f"Feedback: {evaluation.feedback}")
        print(f"Accuracy: {evaluation.accuracy}")
        print(f"Relevance: {evaluation.relevance}")
        print(f"Completeness: {evaluation.completeness}")
        print(f"Grounding: {evaluation.grounding}")

    print("\n=== LAST EVALUATION ===")

    last = memory.get_last_evaluation()

    if last:
        print(f"Iteration: {last.iteration}")
        print(f"Decision: {last.decision}")
        print(f"Feedback: {last.feedback}")

    print("\n=== ITERATION COUNT ===")
    print(memory.get_iterations_len())

    print("\n=== PREVIOUS EVALUATIONS FOR LLM ===")
    print(memory.get_previous_evaluations())


if __name__ == "__main__":
    main()