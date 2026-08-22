from langchain_core.language_models import BaseChatModel
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import SystemMessage, HumanMessage
 
from config.settings import settings


class LLMService:

    def __init__(self):
        endpoint = HuggingFaceEndpoint(
            repo_id=settings.LLM_MODEL,
            huggingfacehub_api_token=settings.HF_TOKEN,
            temperature=settings.LLM_TEMPERATURE,
             max_new_tokens=512,
        )

        self.llm: BaseChatModel = ChatHuggingFace(
            llm=endpoint
        )

    def get_llm(self) -> BaseChatModel:
        return self.llm

    def chat(self, system_message: str, user_message: str) -> str:
        response = self.llm.invoke([
            SystemMessage(content=system_message),
            HumanMessage(content=user_message)
        ])

        return response.content
    