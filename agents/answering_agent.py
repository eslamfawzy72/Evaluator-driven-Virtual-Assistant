# agents/answering_agent.py

import json

from agents.prompts.answering_agent_prompt import AnsweringAgentPrompt
from schemas.answering_input import AnsweringInput
from schemas.answering_output import AnsweringResult
from services.local_llm_service import LocalLLMService


class AnsweringAgent:

    def __init__(self):
        self.llm_service = LocalLLMService()
        self.prompt = AnsweringAgentPrompt()

    def answer(
    self,
    input_data: AnsweringInput,
) -> AnsweringResult:

        evidence_text = self._format_evidence(
            input_data.evidences
        )

        system_message = self.prompt.SYSTEM_PROMPT

        user_message = self.prompt.USER_PROMPT.format(
            query=input_data.query,
            evidences=evidence_text,
            analysis=input_data.analysis,
        )

        response = self.llm_service.chat(
            system_message,
            user_message,
        )

        try:
            answer_data = json.loads(response)

            return AnsweringResult.model_validate(
                answer_data
            )

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"Failed to extract a valid answer: {e}"
            ) from e
            
    @staticmethod
    def _format_evidence(evidences) -> str:

        return "\n\n".join(
            f"""
Document: {evidence.source}
Page: {evidence.page}
Evidence:
{evidence.content}
""".strip()
            for evidence in evidences
        )