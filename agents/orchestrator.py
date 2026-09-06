"""The Orchestrator: wires the three agents into a single question-answering run.

    question -> Retriever Agent  -> list[Evidence]
             -> Analyst Agent    -> AnalystResult (analysis + evidence, which
                                    its retrieve_more tool may have grown by
                                    calling back into the Retriever)
             -> Answering Agent  -> final answer

Each agent stays unaware of the others. The Orchestrator owns the order,
hands each stage's output to the next, and labels failures with the stage
they came from so the API layer can report them usefully.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

from agents.analyzer_agent import AnalystAgent
from agents.answering_agent import AnsweringAgent
from agents.retriever_agent import RetrieverAgent
from schemas.answering_input import AnsweringInput
from schemas.retriever_schema import Evidence

logger = logging.getLogger(__name__)

NO_EVIDENCE_ANSWER = (
    "I could not find anything relevant to this question in the "
    "ingested documents."
)


@dataclass
class OrchestratorResult:
    answer: str
    analysis: str
    evidences: list[Evidence] = field(default_factory=list)


class MultiAgentOrchestrator:

    def __init__(
        self,
        retriever: Optional[RetrieverAgent] = None,
        analyst: Optional[AnalystAgent] = None,
        answerer: Optional[AnsweringAgent] = None,
    ):
        self.retriever = retriever or RetrieverAgent()
        self.analyst = analyst or AnalystAgent()
        self.answerer = answerer or AnsweringAgent()

    def run(
        self,
        question: str,
        conversation_history: Optional[list[str]] = None,
        metadata_filter: Optional[dict] = None,
    ) -> OrchestratorResult:
        """Run the full pipeline for one user question."""
        if not question or not question.strip():
            raise ValueError("Question must not be empty.")

        evidences = self._retrieve(question, conversation_history, metadata_filter)

        # Nothing to reason over -- skip the two LLM stages entirely rather
        # than paying for an analysis of an empty evidence list.
        if not evidences:
            logger.info("No evidence retrieved for question: %r", question)
            return OrchestratorResult(answer=NO_EVIDENCE_ANSWER, analysis="")

        logger.info("Retrieved %d evidence chunks for: %r", len(evidences), question)

        analysis_result = self._analyze(question, evidences)

        if len(analysis_result.evidences) > len(evidences):
            logger.info(
                "Analyst pulled in %d extra chunks via retrieve_more",
                len(analysis_result.evidences) - len(evidences),
            )

        # The Answering Agent sees the evidence the analysis was actually
        # written from -- including anything retrieve_more added -- so it can
        # never be asked to trust an analysis it cannot verify.
        answer = self._answer(
            question,
            analysis_result.evidences,
            analysis_result.analysis,
        )

        return OrchestratorResult(
            answer=answer,
            analysis=analysis_result.analysis,
            evidences=analysis_result.evidences,
        )

    def _retrieve(
        self,
        question: str,
        conversation_history: Optional[list[str]],
        metadata_filter: Optional[dict],
    ) -> list[Evidence]:
        try:
            return self.retriever.retrieve(
                query=question,
                conversation_history=conversation_history,
                metadata_filter=metadata_filter,
            )
        except Exception as exc:
            raise RuntimeError(f"Retrieval failed: {exc}") from exc

    def _analyze(self, question: str, evidences: list[Evidence]):
        try:
            return self.analyst.analyze(query=question, evidences=evidences)
        except Exception as exc:
            raise RuntimeError(f"Analysis failed: {exc}") from exc

    def _answer(
        self,
        question: str,
        evidences: list[Evidence],
        analysis: str,
    ) -> str:
        try:
            result = self.answerer.answer(
                AnsweringInput(
                    query=question,
                    evidences=evidences,
                    analysis=analysis,
                )
            )
        except Exception as exc:
            raise RuntimeError(f"Answer generation failed: {exc}") from exc

        return result.answer
