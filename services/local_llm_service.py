from langchain_ollama import ChatOllama

from config.settings import settings


class LocalLLMService:

    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:3b",
            temperature=settings.LLM_TEMPERATURE,
        )
    
    def get_llm(self):
        return self.llm

    def chat(self, system_message: str, user_message: str) -> str:
        response = self.llm.invoke([
            ("system", system_message),
            ("human", user_message),
        ])

        return response.content