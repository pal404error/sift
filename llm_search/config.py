from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIFT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "llm-search"
    log_level: str = "INFO"

    # Vector store
    vector_store: str = "memory"  # "memory" | "qdrant"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "llm_search"
    vector_dim: int = 384

    # Embedding provider
    embedding_provider: str = "fake"  # "fake" | "openai" | "ollama"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    ollama_embed_url: str = "http://localhost:11434"

    # LLM provider
    llm_provider: str = "fake"  # "fake" | "openai" | "anthropic" | "ollama"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str | None = None
    anthropic_api_key: str | None = None
    ollama_url: str = "http://localhost:11434"
    llm_temperature: float = 0.0

    # Ingestion
    chunk_size: int = 400
    chunk_overlap: int = 64
    max_pages_per_ingest: int = 20
    respect_robots: bool = True
    min_crawl_interval: float = 1.0
    crawl_concurrency: int = 4
    max_fetch_bytes: int = 10 * 1024 * 1024  # cap downloaded page size (SSRF/memory guard)

    # Reranking
    reranker: str = "lexical"  # "none" | "lexical" | "fake" | "cross-encoder"
    rerank_model: str = ""  # cross-encoder model name (empty -> default)
    rerank_multiplier: int = 2

    # Hybrid retrieval (lexical + vector via Reciprocal Rank Fusion)
    hybrid: bool = False
    rrf_k: int = 60
    hybrid_mode: str = "rrf"  # "rrf" (rank fusion) | "weighted" (normalized score blend)
    hybrid_alpha: float = 0.5  # weight on the vector signal when hybrid_mode="weighted"
    hybrid_route: bool = False  # opt-in: bias toward lexical when query has exact-match signals

    # Query expansion (Hypothetical Document Embeddings)
    use_hyde: bool = False

    # Auth / enterprise
    require_auth: bool = False
    auth_method: str = "apikey"  # "apikey" | "oidc"
    api_keys: str = ""  # comma-separated "role:key", e.g. "admin:KEY1,user:KEY2"
    oidc_issuer: str = ""
    oidc_audience: str = ""
    oidc_role_claim: str = "roles"
    audit_log: str = "audit.log"


@lru_cache
def get_settings() -> Settings:
    return Settings()
