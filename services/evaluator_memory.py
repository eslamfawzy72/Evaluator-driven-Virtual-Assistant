from dataclasses import dataclass
from typing import List, Dict, Optional, Literal


@dataclass
class Evaluation:
    question: str
    context: List[Dict[str, str]]
    answer: str

    decision: Literal["accept", "reject"]
    feedback: Optional[str]

    accuracy: float
    relevance: float
    completeness: float
    grounding: float

    iteration: int


class EvaluatorMemory:

    def __init__(self):
        self.evaluations: List[Evaluation] = []

    def add_evaluation(
        self,
        question: str,
        context: List[Dict[str, str]],
        answer: str,
        decision: Literal["accept", "reject"],
        feedback: Optional[str] = None,
        accuracy: float = 0.0,
        relevance: float = 0.0,
        completeness: float = 0.0,
        grounding: float = 0.0,
    ):
        evaluation = Evaluation(
            question=question,
            context=context,
            answer=answer,
            decision=decision,
            feedback=feedback,
            accuracy=accuracy,
            relevance=relevance,
            completeness=completeness,
            grounding=grounding,
            iteration=len(self.evaluations) + 1,
        )

        self.evaluations.append(evaluation)

    def get_evaluations(self) -> List[Evaluation]:
        return self.evaluations

    def get_iterations_len(self) -> int:
        return len(self.evaluations)

    def get_last_evaluation(self) -> Optional[Evaluation]:
        if not self.evaluations:
            return None

        return self.evaluations[-1]

    def get_previous_evaluations(self) -> str:
        if not self.evaluations:
            return ""

        evaluations = []

        for evaluation in self.evaluations:
            evaluations.append(
                f"""Iteration: {evaluation.iteration}
Decision: {evaluation.decision}
Feedback: {evaluation.feedback}
Accuracy: {evaluation.accuracy}
Relevance: {evaluation.relevance}
Completeness: {evaluation.completeness}
Grounding: {evaluation.grounding}"""
            )

        return "\n\n".join(evaluations)

    def clear(self):
        self.evaluations.clear()