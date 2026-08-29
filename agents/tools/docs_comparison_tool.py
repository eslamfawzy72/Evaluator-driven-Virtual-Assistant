import json
from langchain_core.tools import StructuredTool

from agents.prompts.docs_comparison_prompt import DocumentComparisonPrompt
from schemas.comparison_schema import DocumentComparison
from schemas.retriever_schema import Evidence
from services.local_llm_service import LocalLLMService


class DocumentComparisonTool:

    def __init__(self):
        self.llm_service = LocalLLMService()
        self.prompt = DocumentComparisonPrompt()
    def compare_documents(
        self,
        evidences: list[Evidence],
    ) -> DocumentComparison:
        """
        Compare multiple documents and extract their differences.
        """
        document_names = {
        evidence.document_name
        for evidence in evidences
    }

        if len(document_names) < 2:
         raise ValueError(
            "Document comparison requires evidence from at least two documents."
        )
        evidence_text = self._format_evidence(evidences)

        messages = self.prompt.DOCUMENT_COMPARISON_PROMPT.format_messages(
            evidence=evidence_text
        )

        system_message = messages[0].content
        user_message = messages[1].content

        response = self.llm_service.chat(
            system_message,
            user_message,
        )

        try:
            comparison_data = json.loads(response)

            return DocumentComparison.model_validate(comparison_data)

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"Failed to extract a valid document comparison: {e}"
            ) from e

    @staticmethod
    def _format_evidence(evidences: list[Evidence]) -> str:
        return "\n\n".join(
            f"""
Document: {evidence.document_name}
Page: {evidence.page_number}
Evidence:
{evidence.content}
""".strip()
            for evidence in evidences
        )
document_comparison = DocumentComparisonTool()

compare_documents = StructuredTool.from_function(
    func=document_comparison.compare_documents,
    name="compare_documents",
    description="Compare multiple documents and extract their differences.",
)
