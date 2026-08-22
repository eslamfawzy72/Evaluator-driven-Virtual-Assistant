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

settings = Settings()
