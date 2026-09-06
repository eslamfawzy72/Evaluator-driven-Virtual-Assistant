"""Central app settings, loaded from environment variables / .env file.

load_dotenv() reads the .env file (if present) into os.environ, so every
KEY=value line in .env becomes available via os.getenv() below -- exactly
as if it had been set as a real environment variable.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "knowledge_base")

    # llm service settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "Qwen/Qwen3-8B")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

    # LangSmith monitoring -- optional. Tracing only actually activates once
    # a real LANGCHAIN_API_KEY is set; with no key, LangChain silently skips
    # tracing rather than failing, so this is safe to leave unset.
    langsmith_tracing: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    langsmith_api_key: str = os.getenv("LANGCHAIN_API_KEY", "")
    langsmith_project: str = os.getenv("LANGCHAIN_PROJECT", "evaluator-generator-platform")
    langsmith_endpoint: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

settings = Settings()
