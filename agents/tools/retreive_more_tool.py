from langchain_core.tools import StructuredTool

from agents.retriever_agent import RetrieverAgent
from schemas.retriever_schema import Evidence
from schemas.retrieve_more_evidence_schema import RetrieveMoreEvidenceInput

class RetrieveMoreEvidenceTool:

    def __init__(self):
        self.retriever = RetrieverAgent()

    def retrieve(
        self,
        input_data: RetrieveMoreEvidenceInput,
    ) -> list[Evidence]:
        """
        Retrieve more evidence based on a follow-up query.
        """

        return self.retriever.retrieve_more(
            follow_up_query=input_data.follow_up_query,
            already_have=input_data.already_have,
        )



retrieve_more_evidence_tool = RetrieveMoreEvidenceTool()


def _retrieve_more(
    follow_up_query: str,
    already_have: list[Evidence],
) -> list[Evidence]:

    input_data = RetrieveMoreEvidenceInput(
        follow_up_query=follow_up_query,
        already_have=already_have,
    )

    return retrieve_more_evidence_tool.retrieve(
        input_data=input_data,
    )


retrieve = StructuredTool.from_function(
    func=_retrieve_more,
    name="retrieve_more",
    description=(
        "Retrieve additional evidence when the current evidence "
        "is insufficient to answer the user's question."
    ),
)