from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness check for the API."""
    return HealthResponse(status="healthy", version="0.1.0")
    raise NotImplementedError
