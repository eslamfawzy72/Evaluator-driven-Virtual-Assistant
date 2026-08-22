from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class GeneratorAttempt:
    question: str
    context: List[Dict[str, str]]
    answer: str
    feedback: Optional[str] = None
    iteration: int = 1


class GeneratorMemory:

    def __init__(self):
        # Temporary generation attempts for the current workflow
        self.attempts: List[GeneratorAttempt] = []

        # Accepted conversation history
        self.conversation: List[Dict[str, str]] = []

    # -------------------------
    # Generation Attempts
    # -------------------------

    def add_attempt(
        self,
        question: str,
        context: List[Dict[str, str]],
        answer: str,
        feedback: Optional[str] = None,
    ):
        attempt = GeneratorAttempt(
            question=question,
            context=context,
            answer=answer,
            feedback=feedback,
            iteration=len(self.attempts) + 1,
        )

        self.attempts.append(attempt)

    def get_attempts(self) -> List[GeneratorAttempt]:
        return self.attempts

    def get_last_attempt(self) -> Optional[GeneratorAttempt]:
        if not self.attempts:
            return None

        return self.attempts[-1]

    # -------------------------
    # Accepted Conversation
    # -------------------------

    def add_accepted_answer(
        self,
        question: str,
        answer: str,
    ):
        self.conversation.append({
            "question": question,
            "answer": answer,
        })

    def get_conversation(self) -> str:
        if not self.conversation:
            return ""

        conversation = []

        for turn in self.conversation:
            conversation.append(
                f"User: {turn['question']}\n"
                f"Assistant: {turn['answer']}"
            )

        return "\n\n".join(conversation)

    # -------------------------
    # Clear Memory
    # -------------------------

    def clear_attempts(self):
        self.attempts.clear()

    def clear_conversation(self):
        self.conversation.clear()

    def clear(self):
        self.clear_attempts()
        self.clear_conversation()