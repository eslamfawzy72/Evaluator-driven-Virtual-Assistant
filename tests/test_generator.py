from services.generator_agent import GeneratorAgent
from rag.retriever import retrieve


def main():
    generator = GeneratorAgent()

    question = "What is Natural Language Processing?"

    # Retrieve context from the existing RAG pipeline
    context = retrieve(question)

    print("\n=== RETRIEVED CONTEXT ===")

    for item in context:
        print(f"\nSource: {item['source']}")
        print(item["content"])

    # Generate answer using the retrieved context
    answer = generator.generate_answer(
        question=question,
        context=context,
    )

    print("\n=== GENERATED ANSWER ===")
    print(answer)

    print("\n=== GENERATOR ATTEMPTS ===")

    for attempt in generator.memory.get_attempts():
        print(f"Iteration: {attempt.iteration}")
        print(f"Question: {attempt.question}")
        print(f"Answer: {attempt.answer}")


if __name__ == "__main__":
    main()