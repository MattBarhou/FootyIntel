from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from pydantic import ValidationError

from app.config import RAG_DOCUMENTS_PATH, get_embedding_dimension, get_settings


def load_rag_documents(path: Path = RAG_DOCUMENTS_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"RAG documents not found at {path}. "
            "Run: python scripts/generate_rag_documents.py"
        )

    with path.open(encoding="utf-8") as handle:
        documents = json.load(handle)

    if not isinstance(documents, list) or not documents:
        raise ValueError(f"No documents found in {path}")

    for index, document in enumerate(documents):
        if not document.get("id") or not document.get("text"):
            raise ValueError(f"Document at index {index} is missing 'id' or 'text'")

    return documents


def build_pinecone_metadata(document: dict[str, Any]) -> dict[str, str | int | float | bool]:
    """Flatten document metadata for Pinecone (no null/empty values)."""
    metadata: dict[str, str | int | float | bool] = {"text": document["text"]}

    for key, value in document.get("metadata", {}).items():
        if value is None or value == "":
            continue
        if isinstance(value, (str, int, float, bool)):
            metadata[key] = value
        else:
            metadata[key] = str(value)

    return metadata


def _get_pinecone_index(settings=None):
    settings = settings or get_settings()
    client = Pinecone(api_key=settings.pinecone_api_key)
    index_names = {index.name for index in client.list_indexes()}

    if settings.pinecone_index_name not in index_names:
        raise ValueError(
            f"Pinecone index '{settings.pinecone_index_name}' was not found. "
            "Create it in the Pinecone console with dimension "
            f"{get_embedding_dimension(settings.openai_embedding_model)} and metric 'cosine'."
        )

    index = client.Index(settings.pinecone_index_name)
    stats = index.describe_index_stats()
    index_dimension = getattr(stats, "dimension", None)

    expected_dimension = get_embedding_dimension(settings.openai_embedding_model)
    if index_dimension and index_dimension != expected_dimension:
        raise ValueError(
            f"Pinecone index dimension is {index_dimension}, but "
            f"{settings.openai_embedding_model} requires {expected_dimension}."
        )

    return index


def index_rag_documents(force_reindex: bool = False) -> int:
    """Embed RAG documents and upsert them into Pinecone."""
    settings = get_settings()
    documents = load_rag_documents()
    index = _get_pinecone_index(settings)
    namespace = settings.pinecone_namespace

    if force_reindex:
        index.delete(delete_all=True, namespace=namespace)

    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )

    batch_size = settings.rag_index_batch_size
    total = len(documents)
    indexed = 0

    for start in range(0, total, batch_size):
        batch = documents[start : start + batch_size]
        texts = [document["text"] for document in batch]
        vectors = embeddings.embed_documents(texts)

        payload = [
            {
                "id": document["id"],
                "values": vector,
                "metadata": build_pinecone_metadata(document),
            }
            for document, vector in zip(batch, vectors, strict=True)
        ]

        index.upsert(vectors=payload, namespace=namespace)
        indexed += len(batch)

    return indexed


def index_rag_documents_or_http_error(force_reindex: bool = False) -> int:
    """Index documents and translate common failures to HTTP errors."""
    try:
        return index_rag_documents(force_reindex=force_reindex)
    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Missing required environment variables. Set OPENAI_API_KEY and "
                "PINECONE_API_KEY in backend/.env.local (or backend/.env)."
            ),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Indexing failed: {exc}",
        ) from exc
