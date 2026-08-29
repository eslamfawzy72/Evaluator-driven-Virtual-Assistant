from langchain_core.prompts import ChatPromptTemplate


class DataAnalysisPrompt:

    def __init__(self):
        self.DATA_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a data analysis assistant.

Analyze the provided data and answer the analysis query using ONLY
the provided evidence and analysis results.

Your task is to identify:
- calculations
- trends
- patterns
- insights

Rules:
- Do not invent information.
- Do not infer values that are not supported by the evidence.
- Do not perform numerical calculations yourself when a calculated
  result is already provided.
- Use the provided calculation results when interpreting the data.
- Clearly distinguish numerical facts from interpretations.
- Keep insights grounded in the provided evidence.
- If there is insufficient information for a category, return an empty list.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.

Required JSON format:
{{
    "calculations": [],
    "trends": [],
    "patterns": [],
    "insights": []
}}
""",
                ),
                (
                    "human",
                    """
Analysis query:
{query}

Evidence:
{evidence}

Extracted table:
{extracted_table}

Document comparison:
{document_comparison}

Calculated results:
{calculated_results}
Use the available information to perform the requested analysis.
Some of the provided sections may be unavailable. Do not assume
or invent missing information.
Analyze the data and return the result as JSON.
""",
                ),
            ]
        )