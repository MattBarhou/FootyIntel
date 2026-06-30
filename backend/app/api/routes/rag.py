from fastapi import APIRouter

from app.schemas.rag import RagIndexRequest, RagIndexResponse

router = APIRouter(tags=["rag"])


@router.post("/rag/index", response_model=RagIndexResponse)
async def index_rag_documents(request: RagIndexRequest) -> RagIndexResponse:
    """Index or re-index documents for retrieval-augmented generation."""
    raise NotImplementedError
