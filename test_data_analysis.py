from agents.tools.data_analysis import DataAnalysisTool
from schemas.data_analysis_schema import DataAnalysisInput
from schemas.evidence_schema import Evidence
from schemas.table_extractor_schema import ExtractedTable


def main():

    table = ExtractedTable(
        columns=["Model", "Accuracy"],
        rows=[
            ["BERT", "91"],
            ["RoBERTa", "94"],
            ["ALBERT", "89"],
        ],
    )

    evidences = [
        Evidence(
            id="ev_001",
            document_name="paper.pdf",
            page_number=5,
            content="The models achieved the reported accuracy values.",
        )
    ]

    input_data = DataAnalysisInput(
        query=(
    "Analyze the model accuracy and identify which model "
    "has the highest accuracy and any notable pattern."
),
        evidences=evidences,
        extracted_table=table,
    )

    tool = DataAnalysisTool()

    result = tool.analyze(input_data)

    print("\n========== DATA ANALYSIS ==========")
    print(result.model_dump_json(indent=2))
    print("===================================")


if __name__ == "__main__":
    main()