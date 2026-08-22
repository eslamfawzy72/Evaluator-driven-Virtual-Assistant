from services.generator_memory import GeneratorMemory


memory = GeneratorMemory()

memory.add_attempt(
    question="What is NLP?",
    context=[
        {
            "content": "NLP is a branch of artificial intelligence.",
            "source": "intro.pdf",
        }
    ],
    answer="NLP is a branch of artificial intelligence.",
)

memory.add_attempt(
    question="What is AI?",
    context=[
        {
            "content": "AI is a branch of computer science.",
            "source": "intro.pdf",
        }
    ],
    answer="AI is a branch of computer science.",
    feedback="The first answer was too short.",
)

print("All attempts:")
print(memory.get_attempts())

print("\nLast attempt:")
print(memory.get_last_attempt())