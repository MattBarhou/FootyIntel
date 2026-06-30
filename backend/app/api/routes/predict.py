from fastapi import APIRouter

from app.schemas.predict import PredictRequest, PredictResponse
from app.services.prediction_service import predict_match

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
async def predict_match_endpoint(request: PredictRequest) -> PredictResponse:
    """Predict the outcome of a match between two teams."""
    return predict_match(request.home_team, request.away_team)
