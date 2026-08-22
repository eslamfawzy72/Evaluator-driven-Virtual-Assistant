from rag.retriever import retrieve
from services.generator_agent import GeneratorAgent
from services.evaluator_agent import EvaluatorAgent


def main():
    generator = GeneratorAgent()
    evaluator = EvaluatorAgent()

    question = "What is Natural Language Processing?"

    # 1. Retrieve external knowledge
    context = retrieve(question)

    print("\n=== RETRIEVED CONTEXT ===")

    for item in context:
        print(f"\nSource: {item['source']}")
        print(item["content"])

    # 2. Generate answer
    answer = generator.generate_answer(
        question=question,
        context=context,
    )

    print("\n=== GENERATED ANSWER ===")
    print(answer)

    # 3. Evaluate generated answer
    evaluation = evaluator.evaluate(
        question=question,
        context=context,
        answer=answer,
    )

    print("\n=== EVALUATION RESULT ===")
    print(f"Decision: {evaluation.decision}")
    print(f"Feedback: {evaluation.feedback}")
    print(f"Accuracy: {evaluation.accuracy}")
    print(f"Relevance: {evaluation.relevance}")
    print(f"Completeness: {evaluation.completeness}")
    print(f"Grounding: {evaluation.grounding}")

    # 4. Check evaluator memory
    print("\n=== EVALUATOR MEMORY ===")

    for evaluation in evaluator.memory.get_evaluations():
        print(f"\nIteration: {evaluation.iteration}")
        print(f"Decision: {evaluation.decision}")
        print(f"Feedback: {evaluation.feedback}")


if __name__ == "__main__":
    main()