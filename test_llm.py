from services.local_llm_service import LocalLLMService
from agents.tools.calculator_tool import calculator


def main():
    service = LocalLLMService()

    llm = service.get_llm().bind_tools([
        calculator
    ])

    response = llm.invoke(
        "Calculate 91 - 94."
    )

    print("CONTENT:", repr(response.content))
    print("TOOL CALLS:", response.tool_calls)


if __name__ == "__main__":
    main()