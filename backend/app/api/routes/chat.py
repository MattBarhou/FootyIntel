from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_or_http_error

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to the football assistant and receive a reply."""
    return chat_or_http_error(request)
