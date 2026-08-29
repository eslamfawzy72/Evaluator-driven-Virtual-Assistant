from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from schemas.retriever_schema import Evidence
from services.local_llm_service import LocalLLMService

from agents.tools.calculator_tool import calculator
from agents.tools.table_extractor import extract_table
from agents.tools.docs_comparison_tool import compare_documents
from agents.tools.data_analysis import analyze
from agents.tools.retreive_more_tool import retrieve
from agents.prompts.analysis_agent_prompt import AnalystAgentPrompt


class AnalystAgent:

    def __init__(self):
        self.llm_service = LocalLLMService()
        self.prompt = AnalystAgentPrompt()

        self.tools = [
            calculator,
            extract_table,
            compare_documents,
            analyze,
            retrieve,
        ]

        self.tool_map = {
            tool.name: tool
            for tool in self.tools
        }

        self.llm = self.llm_service.get_llm().bind_tools(
            self.tools
        )

    def analyze(
    self,
    query: str,
    evidences: list[Evidence],
) -> str:

        messages = self.prompt.ANALYST_AGENT_PROMPT.format_messages(
            query=query,
            evidences=evidences,
        )

        while True:

            response = self.llm.invoke(messages)

            messages.append(response)

            if not response.tool_calls:
                return response.content

            for tool_call in response.tool_calls:

                tool = self.tool_map[tool_call["name"]]

                result = tool.invoke(
                    tool_call["args"]
                )

                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )


 