from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    # App
    app_name: str = Field(default="PRV Specialist Agent")
    app_port: int = Field(default=8000)
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])

    # Embeddings
    embedding_provider: str = Field(default=os.getenv("EMBEDDING_PROVIDER", "local"))  # 'local' | 'openai'
    sentence_transformer_model: str = Field(default=os.getenv("SENTENCE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    openai_api_key: Optional[str] = Field(default=os.getenv("OPENAI_API_KEY"))
    openai_embedding_model: str = Field(default=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))

    # LLM
    llm_provider: str = Field(default=os.getenv("LLM_PROVIDER", "openai"))  # 'openai' | 'ollama'
    openai_model: str = Field(default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    ollama_model: str = Field(default=os.getenv("OLLAMA_MODEL", "llama3.1"))

    # Vector store
    chroma_persist_path: str = Field(default=os.getenv("CHROMA_PERSIST_PATH", "/workspace/data/chroma"))
    chroma_collection: str = Field(default=os.getenv("CHROMA_COLLECTION", "prv-knowledge"))

    # Chunking
    chunk_size_tokens: int = Field(default=int(os.getenv("CHUNK_SIZE_TOKENS", "400")))
    chunk_overlap_tokens: int = Field(default=int(os.getenv("CHUNK_OVERLAP_TOKENS", "60")))

    # Retrieval/Generation
    top_k: int = Field(default=int(os.getenv("TOP_K", "8")))
    max_context_tokens: int = Field(default=int(os.getenv("MAX_CONTEXT_TOKENS", "6000")))

    # Crawling
    default_max_pages: int = Field(default=int(os.getenv("DEFAULT_MAX_PAGES", "100")))
    default_allowed_domains: List[str] = Field(default_factory=list)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()