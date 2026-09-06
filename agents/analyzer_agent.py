"""The Analyst Agent: reasons over the evidence the Retriever found.

Runs a tool-calling loop until the LLM stops asking for tools. One of its
tools -- retrieve_more -- calls back into the Retriever Agent, so the
evidence set can grow while the loop runs. Every new chunk is collected and
returned alongside the analysis, so the Answering Agent sees exactly the
evidence the analysis was written from.
"""
from langchain_core.messages import HumanMessage, ToolMessage

from schemas.analysis_agent_schema import AnalystResult
from schemas.retriever_schema import Evidence
from services.local_llm_service import LocalLLMService

from agents.tools.calculator_tool import calculator
from agents.tools.table_extractor import extract_table
from agents.tools.docs_comparison_tool import compare_documents
from agents.tools.data_analysis import analyze
from agents.tools.retreive_more_tool import retrieve
from agents.prompts.analysis_agent_prompt import AnalystAgentPrompt


# Hard stop on the tool loop: a local model that keeps re-calling the same
# tool would otherwise hang the request forever.
MAX_TOOL_ITERATIONS = 8

# Which argument each tool expects the working evidence in. Used only to
# backfill the argument when the model leaves it out -- see _run_tool().
EVIDENCE_ARGUMENTS = {
    "extract_table": "evidences",
    "compare_documents": "evidences",
    "analyze": "evidences",
    "retrieve_more": "already_have",
}


class AnalystAgent:

    def __init__(self):
        self.llm_service = LocalLLMService(model="qwen3:8b")
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
    ) -> AnalystResult:
        """Main entry point -- the Orchestrator calls this.

        Returns the analysis together with the evidence it was based on,
        which includes anything the retrieve_more tool pulled in mid-loop.
        """
        messages = self.prompt.ANALYST_AGENT_PROMPT.format_messages(
            query=query,
            evidences=evidences,
        )

        collected = list(evidences)

        for iteration in range(1, MAX_TOOL_ITERATIONS + 1):

            response = self.llm.invoke(messages)

            print("\n========== LLM RESPONSE ==========")
            print("Iteration:", iteration)
            print("Content:", repr(response.content))
            print("Tool calls:", response.tool_calls)
            print("===================================")

            messages.append(response)

            if not response.tool_calls:
                return AnalystResult(
                    analysis=response.content,
                    evidences=collected,
                )

            for tool_call in response.tool_calls:

                print("\n========== TOOL CALL ==========")
                print("Tool:", tool_call["name"])
                print("Arguments:", tool_call["args"])
                print("===============================")

                result = self._run_tool(tool_call, collected)

                print("\n========== TOOL RESULT ==========")
                print(result)
                print("=================================")

                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

        # Tool budget spent. Ask once more with the unbound LLM so the model
        # cannot request another tool and the loop always ends with an
        # analysis rather than an exception.
        messages.append(
            HumanMessage(
                content=(
                    "You have used all available tool calls. Write the final "
                    "analysis now, using only the evidence and tool results "
                    "above. Do not request any more tools."
                )
            )
        )

        final_response = self.llm_service.get_llm().invoke(messages)

        return AnalystResult(
            analysis=final_response.content,
            evidences=collected,
        )

    def _run_tool(self, tool_call: dict, collected: list[Evidence]):
        """Invoke one tool call and keep the evidence list up to date.

        Tool failures are returned to the model as text instead of raised:
        a bad argument or an unparseable LLM sub-response then costs one
        iteration and can be corrected, rather than killing the run.
        """
        name = tool_call["name"]
        tool = self.tool_map.get(name)

        if tool is None:
            return f"Error: '{name}' is not an available tool."

        arguments = dict(tool_call.get("args") or {})

        # The prompt asks the model to pass the evidence it is working on,
        # but a local model regularly omits it. Backfilling from what we
        # already hold keeps a forgotten argument from failing validation.
        evidence_argument = EVIDENCE_ARGUMENTS.get(name)

        if evidence_argument and not arguments.get(evidence_argument):
            # A copy: collected keeps growing as retrieve_more returns chunks,
            # and a tool must not see the list change under it.
            arguments[evidence_argument] = list(collected)

        try:
            result = tool.invoke(arguments)
        except Exception as exc:
            return f"Error running '{name}': {exc}"

        if name == "retrieve_more":
            self._collect_new_evidence(result, collected)

        return result

    @staticmethod
    def _collect_new_evidence(result, collected: list[Evidence]) -> None:
        """Append evidence returned by retrieve_more to the working set.

        retrieve_more already drops chunks the Analyst passed as
        already_have, but it can be called several times per run -- dedupe
        against everything collected so far before growing the list.
        """
        if not isinstance(result, list):
            return

        seen = {evidence.content.strip() for evidence in collected}

        for evidence in result:
            if not isinstance(evidence, Evidence):
                continue

            normalized = evidence.content.strip()

            if normalized and normalized not in seen:
                collected.append(evidence)
                seen.add(normalized)
