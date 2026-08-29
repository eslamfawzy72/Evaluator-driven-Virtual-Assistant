from langchain_core.prompts import ChatPromptTemplate
class TableExtractorPrompt:
    def __init__(self):
        self.TABLE_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a table extraction assistant.

Your task is to extract a table from the provided document evidence.

Rules:
- Extract only information that appears in the evidence.
- Do not invent, infer, or calculate values.
- Preserve values exactly as they appear in the evidence.
- Identify the table columns.
- Represent each row as a list of values.
- Every row must contain exactly the same number of values as the columns.
- The evidence may come from multiple documents or pages.
- Combine evidence only when it clearly belongs to the same table.
- Do not combine unrelated tables.
- If no table can be identified, return empty columns and rows.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.

Required JSON format:
{{
    "columns": ["column1", "column2"],
    "rows": [
        ["value1", "value2"],
        ["value3", "value4"]
    ]
}}
""",
                ),
                (
                    "human",
                    """
Evidence:

{evidence}

Extract the table and return the result as JSON.
""",
                ),
            ]
        )