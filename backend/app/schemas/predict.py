from pydantic import BaseModel


class PredictRequest(BaseModel):
    home_team: str
    away_team: str


class PredictResponse(BaseModel):
    home_team: str
    away_team: str
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    predicted_result: str  # "H" | "D" | "A"
