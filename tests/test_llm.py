from services.llm_service import LLMService


llm_service = LLMService()

response = llm_service.chat(
    "What is Natural Language Processing?"
)

print(response)