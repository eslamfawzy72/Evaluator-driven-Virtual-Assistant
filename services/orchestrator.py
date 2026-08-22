from dataclasses import dataclass

from rag.retriever import retrieve
from services.generator_agent import GeneratorAgent
from services.evaluator_agent import EvaluatorAgent


@dataclass
class OrchestratorResult:
    answer: str
    decision: str
    iterations: int
    feedback: str | None = None


class QAOrchestrator:

    MAX_ITERATIONS = 4

    def __init__(self):
        self.generator = GeneratorAgent()
        self.evaluator = EvaluatorAgent()

    def run(self, question: str) -> OrchestratorResult:

        context = retrieve(question)

        feedback = None

        for iteration in range(1, self.MAX_ITERATIONS + 1):

            answer = self.generator.generate_answer(
                question=question,
                context=context,
                feedback=feedback,
            )

            evaluation = self.evaluator.evaluate(
                question=question,
                context=context,
                answer=answer,
            )

            if evaluation.decision == "accept":

                self.generator.memory.add_accepted_answer(
                    question=question,
                    answer=answer,
                )

                return OrchestratorResult(
                    answer=answer,
                    decision="accept",
                    iterations=iteration,
                    feedback=evaluation.feedback,
                )

            feedback = evaluation.feedback

        return OrchestratorResult(
            answer=answer,
            decision="reject",
            iterations=self.MAX_ITERATIONS,
            feedback=feedback,
        )