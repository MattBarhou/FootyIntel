from fastapi import APIRouter

from app.schemas.rag import RagIndexRequest, RagIndexResponse
from app.services.rag_service import index_rag_documents_or_http_error

router = APIRouter(tags=["rag"])


@router.post("/rag/index", response_model=RagIndexResponse)
def index_rag_documents_route(request: RagIndexRequest) -> RagIndexResponse:
    """Index or re-index documents for retrieval-augmented generation."""
    documents_indexed = index_rag_documents_or_http_error(
        force_reindex=request.force_reindex
    )
    status = "reindexed" if request.force_reindex else "indexed"
    return RagIndexResponse(status=status, documents_indexed=documents_indexed)
