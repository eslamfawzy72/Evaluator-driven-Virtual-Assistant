import json

from agents.prompts.table_extractor_prompt import TableExtractorPrompt
from schemas.evidence_schema import Evidence
from schemas.table_extractor_schema import ExtractedTable
from services.local_llm_service import LocalLLMService

class TableExtractor:

    def __init__(self):
        self.llm_service = LocalLLMService()
        self.prompt = TableExtractorPrompt()

    def extract_table(self, evidences: list[Evidence]) -> ExtractedTable:
        evidence_text = self._format_evidence(evidences)
        messages = self.prompt.TABLE_EXTRACTION_PROMPT.format_messages(
        evidence=evidence_text
    )

        system_message = messages[0].content
        user_message =messages[1].content

        response = self.llm_service.chat(
            system_message,
            user_message
        )
        print("\n========== RAW LLM RESPONSE ==========")
        print(response)
        print("======================================\n")
        try:
            table_data = json.loads(response)

            return ExtractedTable.model_validate(table_data)

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"Failed to extract a valid table: {e}"
            ) from e

    @staticmethod
    def _format_evidence(evidences: list[Evidence]) -> str:
        return "\n\n".join(
            f"""
Evidence ID: {evidence.id}
Document: {evidence.document_name}
Page: {evidence.page_number}
Content:
{evidence.content}
""".strip()
            for evidence in evidences
        )