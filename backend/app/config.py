from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"
RAG_DOCUMENTS_PATH = PROCESSED_DIR / "rag_documents.json"

# Prefer .env.local (Next-style) over .env when both exist.
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env.local", override=True)

EMBEDDING_DIMENSIONS: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", BACKEND_DIR / ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(validation_alias="OPENAI_API_KEY")
    pinecone_api_key: str = Field(validation_alias="PINECONE_API_KEY")
    pinecone_index_name: str = Field(
        default="footyintel",
        validation_alias="PINECONE_INDEX_NAME",
    )
    pinecone_namespace: str = Field(
        default="rag",
        validation_alias="PINECONE_NAMESPACE",
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_chat_model: str = Field(
        default="gpt-4o-mini",
        validation_alias="OPENAI_CHAT_MODEL",
    )
    rag_index_batch_size: int = Field(
        default=100,
        validation_alias="RAG_INDEX_BATCH_SIZE",
    )
    rag_top_k: int = Field(
        default=6,
        validation_alias="RAG_TOP_K",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def get_embedding_dimension(model: str) -> int:
    if model in EMBEDDING_DIMENSIONS:
        return EMBEDDING_DIMENSIONS[model]
    raise ValueError(
        f"Unknown embedding model '{model}'. "
        f"Supported models: {', '.join(sorted(EMBEDDING_DIMENSIONS))}"
    )
