from langchain_core.prompts import ChatPromptTemplate


class CalculationPlanPrompt:

    def __init__(self):
        self.CALCULATION_PLAN_PROMPT = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a calculation planning assistant.

Your task is to convert the analysis request into a structured
calculation plan using the provided table.

Available operations:
- mean
- median
- min
- max
- range
- count
- difference
- percentage_change

Rules:
- Only create calculations that are required by the analysis request.
- Use only columns that exist in the provided table.
- Do not perform any calculations yourself.
- Do not invent column names or values.
- For difference and percentage_change, specify the values being compared
  when the request identifies them.
- If the requested analysis does not require numerical calculations,
  return an empty calculations list.
- If the requested calculation cannot be performed from the table,
  return an empty calculations list.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.

Required JSON format:
{{
    "calculations": [
        {{
            "operation": "mean",
            "column": "Accuracy",
            "second_column": null,
            "first_value": null,
            "second_value": null
        }}
    ]
}}
""",
                ),
                (
                    "human",
                    """
Analysis request:
{analysis_request}

Available table:
{table}

Create the calculation plan.
""",
                ),
            ]
        )