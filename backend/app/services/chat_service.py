from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import ValidationError

from app.config import get_settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.query_parser import ParsedQuery, parse_query
from app.services.rag_service import _get_pinecone_index
from app.services.season_rank_service import (
    format_season_rank_context,
    rank_team_seasons,
)

SYSTEM_PROMPT = """You are FootyIntel, a Premier League football assistant.

Answer the user's question using ONLY the provided context documents.
If the context does not contain enough information, say you do not have enough
data in the knowledge base to answer confidently.
Be concise, factual, and specific. Prefer season stats, form, home/away splits,
head-to-head records, and match details from the context when available.
Do not invent scores or statistics.
"""


def build_pinecone_filter(parsed: ParsedQuery) -> dict[str, Any] | None:
    """Build a Pinecone metadata filter from the parsed question."""
    clauses: list[dict[str, Any]] = []

    if parsed.intent == "h2h" and len(parsed.teams) >= 2:
        team_a, team_b = sorted(parsed.teams[:2])
        clauses.append({"type": {"$eq": "h2h_summary"}})
        clauses.append(
            {
                "$or": [
                    {
                        "$and": [
                            {"team_a": {"$eq": team_a}},
                            {"team_b": {"$eq": team_b}},
                        ]
                    },
                    {
                        "$and": [
                            {"team_a": {"$eq": team_b}},
                            {"team_b": {"$eq": team_a}},
                        ]
                    },
                ]
            }
        )
        return {"$and": clauses}

    if parsed.intent == "home_away":
        clauses.append({"type": {"$eq": "home_away_summary"}})
    elif parsed.intent == "form":
        clauses.append({"type": {"$eq": "team_form"}})
    elif parsed.intent == "season":
        clauses.append(
            {
                "type": {
                    "$in": [
                        "season_summary",
                        "home_away_summary",
                        "team_form",
                    ]
                }
            }
        )

    if parsed.seasons:
        if len(parsed.seasons) == 1:
            clauses.append({"season": {"$eq": parsed.seasons[0]}})
        else:
            clauses.append({"season": {"$in": parsed.seasons}})

    if parsed.teams:
        team_filters: list[dict[str, Any]] = []
        for team in parsed.teams:
            team_filters.extend(
                [
                    {"team": {"$eq": team}},
                    {"home_team": {"$eq": team}},
                    {"away_team": {"$eq": team}},
                    {"team_a": {"$eq": team}},
                    {"team_b": {"$eq": team}},
                    {"opponent": {"$eq": team}},
                ]
            )
        clauses.append({"$or": team_filters})

    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def retrieve_context(
    query: str,
    *,
    top_k: int | None = None,
    metadata_filter: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Embed the query and retrieve the most relevant Pinecone documents."""
    settings = get_settings()
    k = top_k or settings.rag_top_k

    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )
    query_vector = embeddings.embed_query(query)
    index = _get_pinecone_index(settings)

    query_kwargs: dict[str, Any] = {
        "vector": query_vector,
        "top_k": k,
        "namespace": settings.pinecone_namespace,
        "include_metadata": True,
    }
    if metadata_filter:
        query_kwargs["filter"] = metadata_filter

    response = index.query(**query_kwargs)
    matches = getattr(response, "matches", None) or []
    contexts: list[dict[str, Any]] = []

    for match in matches:
        metadata = getattr(match, "metadata", None) or {}
        text = metadata.get("text")
        if not text:
            continue
        contexts.append(
            {
                "id": getattr(match, "id", ""),
                "score": float(getattr(match, "score", 0.0) or 0.0),
                "text": text,
                "metadata": {
                    key: value
                    for key, value in metadata.items()
                    if key != "text"
                },
            }
        )

    return contexts


def retrieve_with_fallback(query: str, parsed: ParsedQuery) -> list[dict[str, Any]]:
    """Retrieve with metadata filters, falling back to unfiltered search."""
    settings = get_settings()
    metadata_filter = build_pinecone_filter(parsed)
    top_k = settings.rag_top_k

    if parsed.intent in {"h2h", "home_away", "season", "form"}:
        top_k = max(top_k, 8)
    if len(parsed.teams) >= 2 or parsed.seasons:
        top_k = max(top_k, 8)

    contexts = retrieve_context(
        query,
        top_k=top_k,
        metadata_filter=metadata_filter,
    )
    if contexts or not metadata_filter:
        return contexts

    # Relaxed retry: keep team/season constraints but drop type filters.
    relaxed = ParsedQuery(
        teams=parsed.teams,
        seasons=parsed.seasons,
        intent="general",
    )
    relaxed_filter = build_pinecone_filter(relaxed)
    contexts = retrieve_context(
        query,
        top_k=top_k,
        metadata_filter=relaxed_filter,
    )
    if contexts or not relaxed_filter:
        return contexts

    return retrieve_context(query, top_k=top_k)


def _format_context(contexts: list[dict[str, Any]]) -> str:
    if not contexts:
        return "No relevant context documents were retrieved."

    blocks: list[str] = []
    for i, item in enumerate(contexts, start=1):
        meta = item.get("metadata", {})
        header_parts = [f"Document {i}"]
        if meta.get("type"):
            header_parts.append(f"type={meta['type']}")
        if meta.get("season"):
            header_parts.append(f"season={meta['season']}")
        if meta.get("team"):
            header_parts.append(f"team={meta['team']}")
        if meta.get("team_a") and meta.get("team_b"):
            header_parts.append(f"h2h={meta['team_a']} vs {meta['team_b']}")
        if meta.get("home_team") and meta.get("away_team"):
            header_parts.append(f"match={meta['home_team']} vs {meta['away_team']}")
        header = " | ".join(header_parts)
        blocks.append(f"[{header}]\n{item['text']}")

    return "\n\n".join(blocks)


def generate_reply(message: str, contexts: list[dict[str, Any]]) -> str:
    """Generate an LLM reply grounded in retrieved context."""
    settings = get_settings()
    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )

    context_block = _format_context(contexts)
    user_prompt = (
        f"Context documents:\n{context_block}\n\n"
        f"User question:\n{message.strip()}\n\n"
        "Answer based on the context above."
    )

    response = llm.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )
    content = getattr(response, "content", None)
    if isinstance(content, str) and content.strip():
        return content.strip()
    return "I could not generate a response from the retrieved context."


def chat(request: ChatRequest) -> ChatResponse:
    message = (request.message or "").strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty")

    conversation_id = request.conversation_id or str(uuid.uuid4())
    parsed = parse_query(message)

    contexts: list[dict[str, Any]] = []

    if parsed.intent == "season_rank" and parsed.teams and parsed.rank_mode:
        rank_result = rank_team_seasons(
            parsed.teams[0],
            mode=parsed.rank_mode,
            years=parsed.years or 5,
        )
        contexts.append(
            {
                "id": "season_rank_tool",
                "score": 1.0,
                "text": format_season_rank_context(rank_result),
                "metadata": {
                    "type": "season_rank_tool",
                    "team": parsed.teams[0],
                },
            }
        )
        # Add a little RAG context around the selected season when possible.
        if rank_result.get("selected"):
            season_contexts = retrieve_context(
                f"{parsed.teams[0]} {rank_result['selected']['season']} season summary",
                top_k=4,
                metadata_filter={
                    "$and": [
                        {"team": {"$eq": parsed.teams[0]}},
                        {"season": {"$eq": rank_result["selected"]["season"]}},
                        {
                            "type": {
                                "$in": [
                                    "season_summary",
                                    "home_away_summary",
                                    "team_form",
                                ]
                            }
                        },
                    ]
                },
            )
            contexts.extend(season_contexts)
    else:
        contexts = retrieve_with_fallback(message, parsed)

    reply = generate_reply(message, contexts)
    return ChatResponse(reply=reply, conversation_id=conversation_id)


def chat_or_http_error(request: ChatRequest) -> ChatResponse:
    try:
        return chat(request)
    except HTTPException:
        raise
    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Missing required environment variables. Set OPENAI_API_KEY and "
                "PINECONE_API_KEY in backend/.env.local (or backend/.env)."
            ),
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {exc}",
        ) from exc
