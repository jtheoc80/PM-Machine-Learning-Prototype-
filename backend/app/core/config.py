from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Load from .env by default as well as process env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
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
    vector_store_provider: str = Field(default=os.getenv("VECTOR_STORE_PROVIDER", "chroma"))  # 'chroma' | 'pgvector'
    chroma_persist_path: str = Field(default=os.getenv("CHROMA_PERSIST_PATH", "/workspace/data/chroma"))
    chroma_collection: str = Field(default=os.getenv("CHROMA_COLLECTION", "prv-knowledge"))

    # Supabase / Postgres (pgvector)
    supabase_url: Optional[str] = Field(default=os.getenv("SUPABASE_URL"))
    supabase_anon_key: Optional[str] = Field(default=os.getenv("SUPABASE_ANON_KEY"))
    supabase_service_role_key: Optional[str] = Field(default=os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

    # Prefer DATABASE_URL (e.g. from Supabase Dashboard). If not set, build from parts
    database_url: Optional[str] = Field(default=os.getenv("DATABASE_URL"))
    postgres_host: Optional[str] = Field(default=os.getenv("POSTGRES_HOST"))
    postgres_port: int = Field(default=int(os.getenv("POSTGRES_PORT", "5432")))
    postgres_db: Optional[str] = Field(default=os.getenv("POSTGRES_DB"))
    postgres_user: Optional[str] = Field(default=os.getenv("POSTGRES_USER"))
    postgres_password: Optional[str] = Field(default=os.getenv("POSTGRES_PASSWORD"))

    # Embedding/vector settings for pgvector
    embedding_dim: int = Field(default=int(os.getenv("EMBEDDING_DIM", "384")))  # 384 (MiniLM) or 1536 (OpenAI small), etc.
    pgvector_distance: str = Field(default=os.getenv("PGVECTOR_DISTANCE", "cosine"))  # 'cosine' | 'l2' | 'ip'
    pgvector_ivfflat_lists: int = Field(default=int(os.getenv("PGVECTOR_IVFFLAT_LISTS", "100")))

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