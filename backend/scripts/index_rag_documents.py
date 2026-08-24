#!/usr/bin/env python3
"""Embed RAG documents and upsert them into Pinecone."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.config import RAG_DOCUMENTS_PATH, get_settings
from app.services.rag_service import index_rag_documents, load_rag_documents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Embed RAG documents and upsert them into Pinecone."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing vectors in the namespace before indexing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        settings = get_settings()
    except Exception as exc:
        print(
            "Missing required environment variables. "
            "Set OPENAI_API_KEY and PINECONE_API_KEY in backend/.env.local "
            "(or backend/.env)."
        )
        raise SystemExit(1) from exc

    documents = load_rag_documents(RAG_DOCUMENTS_PATH)

    print(f"Loaded {len(documents)} documents from {RAG_DOCUMENTS_PATH}")
    print(f"Target index: {settings.pinecone_index_name}")
    print(f"Namespace: {settings.pinecone_namespace}")
    print(f"Embedding model: {settings.openai_embedding_model}")

    if args.force:
        print("Force reindex enabled: clearing namespace before upsert.")

    indexed = index_rag_documents(force_reindex=args.force)
    print(f"Indexed {indexed} documents successfully.")


if __name__ == "__main__":
    main()
