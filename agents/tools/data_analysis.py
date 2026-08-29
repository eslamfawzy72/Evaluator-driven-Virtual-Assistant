import json

from agents.prompts.data_analysis_prompt import DataAnalysisPrompt
from schemas.calculation_schema import Calculation, CalculationPlan
from schemas.data_analysis_schema import DataAnalysisInput
from schemas.data_analysis_schema import DataAnalysisResult
from schemas.table_extractor_schema import ExtractedTable
from services.local_llm_service import LocalLLMService
from agents.prompts.calculation_plan_prompt import CalculationPlanPrompt
from agents.tools.calculator_tool import calculator


class DataAnalysisTool:

    def __init__(self):
        self.llm_service = LocalLLMService()
        self.prompt = DataAnalysisPrompt()
        self.calculation_plan_prompt = CalculationPlanPrompt()

    def _get_column_values(
    self,
    table: ExtractedTable,
    column_name: str,
) -> list[str]:

        try:
            column_index = table.columns.index(column_name)
        except ValueError as exc:
            raise ValueError(
                f"Column '{column_name}' was not found in the table."
            ) from exc

        values = []

        for row in table.rows:
            if column_index >= len(row):
                raise ValueError(
                    f"Row does not contain column '{column_name}'."
                )

            value = row[column_index].strip()

            if not value:
                raise ValueError(
                    f"Empty value found in column '{column_name}'."
                )

            values.append(value)

        return values
    def _create_calculation_plan(
    self,
    input_data: DataAnalysisInput,
) -> CalculationPlan:

        if input_data.extracted_table is None:
            return CalculationPlan(calculations=[])

        table = input_data.extracted_table.model_dump_json()

        messages = self.calculation_plan_prompt.CALCULATION_PLAN_PROMPT.format_messages(
            analysis_request=input_data.query,
            table=table,
        )

        system_message = messages[0].content
        user_message = messages[1].content

        response = self.llm_service.chat(
            system_message,
            user_message,
        )

        try:
            plan_data = json.loads(response)

            return CalculationPlan.model_validate(plan_data)

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"Failed to create a valid calculation plan: {e}"
            ) from e
    
    
    @staticmethod
    def _parse_numeric_value(value: str) -> float:

        value = value.strip()
        value = value.replace(",", "")

        if value.endswith("%"):
            value = value[:-1]

        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(
                f"Value '{value}' is not numeric."
            ) from exc
        
    def _execute_calculation(
    self,
    calculation: Calculation,
    table: ExtractedTable,
) -> str:

        values = self._get_column_values(
            table,
            calculation.column,
        )

        if calculation.operation == "mean":
            numeric_values = [
                self._parse_numeric_value(value)
                for value in values
            ]

            expression = (
                f"average({', '.join(map(str, numeric_values))})"
            )

        elif calculation.operation == "median":
            expression = self._build_median_expression(
                values
            )

        elif calculation.operation == "min":
            numeric_values = [
                self._parse_numeric_value(value)
                for value in values
            ]

            result = min(numeric_values)

            return f"Minimum {calculation.column} = {result}"

        elif calculation.operation == "max":
            numeric_values = [
                self._parse_numeric_value(value)
                for value in values
            ]

            result = max(numeric_values)

            return f"Maximum {calculation.column} = {result}"

        elif calculation.operation == "count":
            return f"{calculation.column} count = {len(values)}"

        elif calculation.operation == "range":
            numeric_values = [
                self._parse_numeric_value(value)
                for value in values
            ]

            minimum = min(numeric_values)
            maximum = max(numeric_values)

            expression = f"{maximum} - {minimum}"

        elif calculation.operation in {
            "difference",
            "percentage_change",
        }:
            expression = self._build_comparison_expression(
                calculation,
                table,
            )

        else:
            raise ValueError(
                f"Unsupported calculation: {calculation.operation}"
            )

        result = calculator.invoke(expression)

        return (
            f"{calculation.operation} of "
            f"{calculation.column} = {result}"
        )
    
    def _build_comparison_expression(
    self,
    calculation: Calculation,
    table: ExtractedTable,
) -> str:

        if not calculation.first_value or not calculation.second_value:
            raise ValueError(
                "Comparison requires first_value and second_value."
            )

        column_index = table.columns.index(calculation.column)

        first_row = next(
            row for row in table.rows
            if calculation.first_value in row
        )

        second_row = next(
            row for row in table.rows
            if calculation.second_value in row
        )

        first_value = self._parse_numeric_value(
            first_row[column_index]
        )

        second_value = self._parse_numeric_value(
            second_row[column_index]
        )

        if calculation.operation == "difference":
            return f"{first_value} - {second_value}"

        if calculation.operation == "percentage_change":
            return f"percentage({first_value}, {second_value})"

        raise ValueError(
            f"Unsupported comparison operation: {calculation.operation}"
        )
        
    def analyze(self, input_data: DataAnalysisInput) -> DataAnalysisResult:

        evidence_text = self._format_evidence(
            input_data.evidences
        )

        extracted_table = (
            input_data.extracted_table.model_dump_json()
            if input_data.extracted_table
            else "None"
        )

        document_comparison = (
            input_data.document_comparison.model_dump_json()
            if input_data.document_comparison
            else "None"
        )

        calculated_results = self._calculate(
            input_data
        )

        messages = self.prompt.DATA_ANALYSIS_PROMPT.format_messages(
            query=input_data.query,
            evidence=evidence_text,
            extracted_table=extracted_table,
            document_comparison=document_comparison,
            calculated_results=calculated_results,
        )

        system_message = messages[0].content
        user_message = messages[1].content

        response = self.llm_service.chat(
            system_message,
            user_message,
        )

        try:
            analysis_data = json.loads(response)

            return DataAnalysisResult.model_validate(
                analysis_data
            )

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"Failed to extract valid data analysis: {e}"
            ) from e

    @staticmethod
    def _format_evidence(evidences) -> str:
        return "\n\n".join(
            f"""
Document: {evidence.document_name}
Page: {evidence.page_number}
Evidence:
{evidence.content}
""".strip()
            for evidence in evidences
        )

    def _calculate(self, input_data: DataAnalysisInput) -> str:

        if input_data.extracted_table is None:
            return "No structured table was provided. No calculations performed."

        calculation_plan = self._create_calculation_plan(input_data)

        if not calculation_plan.calculations:
            return "No calculations required."

        results = []

        for calculation in calculation_plan.calculations:
            result = self._execute_calculation(
                calculation,
                input_data.extracted_table,
            )

            results.append(result)

        return "\n".join(results)