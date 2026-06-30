from fastapi import APIRouter

from app.schemas.compare import CompareRequest, CompareResponse
from app.services.prediction_service import compare_teams

router = APIRouter(tags=["compare"])


@router.post("/compare", response_model=CompareResponse)
async def compare_teams_endpoint(request: CompareRequest) -> CompareResponse:
    """Compare rolling season stats between two teams."""
    return compare_teams(request)
