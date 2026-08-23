from dataclasses import dataclass

from rag.retriever import retrieve
from services.generator_agent import GeneratorAgent
from services.evaluator_agent import EvaluatorAgent
from cache.redis_cache import get_cached_answer, get_knowledge_version, set_cached_answer

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

        # Live version tag -- bumped automatically whenever ingest() stores
        # new content (see rag/vector_store.py), so a cached answer from
        # before the knowledge base changed is never served as current.
        knowledge_version = get_knowledge_version()

        # 1. QA cache
        cached = get_cached_answer(question, knowledge_version)

        if cached:
            return OrchestratorResult(
                answer=cached["answer"],
                decision=cached["decision"],
                iterations=cached["iterations"],
                feedback=cached.get("feedback"),
            )

        try:
            context = retrieve(question)

        except Exception as e:
            raise ValueError(f"Error occurred while retrieving context: {e}")

        feedback = None

        for iteration in range(1, self.MAX_ITERATIONS + 1):

            try:
                answer = self.generator.generate_answer(
                    question=question,
                    context=context,
                    feedback=feedback,
                )
            except Exception as e:
                raise ValueError(f"Error occurred while generating answer: {e}")

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

                result= OrchestratorResult(
                    answer=answer,
                    decision="accept",
                    iterations=iteration,
                    feedback=evaluation.feedback,
                )
                set_cached_answer(
                question,
                knowledge_version,
                {
                    "answer": result.answer,
                    "decision": result.decision,
                    "iterations": result.iterations,
                    "feedback": result.feedback,
                },
            )
                return result

            feedback = evaluation.feedback

        return OrchestratorResult(
            answer=answer,
            decision="reject",
            iterations=self.MAX_ITERATIONS,
            feedback=feedback,
        )