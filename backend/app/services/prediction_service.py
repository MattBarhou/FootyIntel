from __future__ import annotations

from functools import lru_cache

from fastapi import HTTPException

from app.ml.data_loader import get_latest_season, load_matches, normalize_team_name
from app.ml.features import LABEL_TO_RESULT, build_inference_features, get_team_season_stats
from app.ml.train import load_metadata, load_model
from app.schemas.compare import CompareRequest, CompareResponse, TeamStats
from app.schemas.predict import PredictResponse


@lru_cache(maxsize=1)
def _get_model():
    return load_model(), load_metadata()


def predict_match(home_team: str, away_team: str) -> PredictResponse:
    home = normalize_team_name(home_team)
    away = normalize_team_name(away_team)

    if home is None:
        raise HTTPException(status_code=404, detail=f"Team not found: {home_team}")
    if away is None:
        raise HTTPException(status_code=404, detail=f"Team not found: {away_team}")
    if home == away:
        raise HTTPException(status_code=422, detail="Home and away teams must be different")

    pipeline, metadata = _get_model()
    matches = load_matches()
    features = build_inference_features(matches, home, away)

    feature_columns = metadata["feature_columns"]
    X = features[feature_columns]

    probabilities = pipeline.predict_proba(X)[0]
    predicted_idx = int(probabilities.argmax())

    return PredictResponse(
        home_team=home,
        away_team=away,
        home_win_probability=round(float(probabilities[0]), 4),
        draw_probability=round(float(probabilities[1]), 4),
        away_win_probability=round(float(probabilities[2]), 4),
        predicted_result=LABEL_TO_RESULT[predicted_idx],
    )


def _comparison_score(stats: dict[str, float]) -> float:
    return (
        stats["ppg"] * 0.4
        + stats["goal_diff"] * 0.3
        + stats["shots_on_target"] * 0.2
        + stats["win_rate"] * 0.1
    )


def _build_comparison_summary(
    team_a: str,
    team_b: str,
    stats_a: dict[str, float],
    stats_b: dict[str, float],
    better: str,
) -> str:
    if better == "even":
        return f"{team_a} and {team_b} are performing at a similar level this season."

    leader = team_a if better == "team_a" else team_b
    trailer = team_b if better == "team_a" else team_a
    leader_stats = stats_a if better == "team_a" else stats_b
    trailer_stats = stats_b if better == "team_a" else stats_a

    edges: list[str] = []
    if leader_stats["ppg"] > trailer_stats["ppg"] + 0.15:
        edges.append("points per game")
    if leader_stats["goal_diff"] > trailer_stats["goal_diff"] + 0.1:
        edges.append("goal difference")
    if leader_stats["shots_on_target"] > trailer_stats["shots_on_target"] + 0.3:
        edges.append("shots on target")
    if leader_stats["win_rate"] > trailer_stats["win_rate"] + 0.05:
        edges.append("win rate")

    edge_text = ", ".join(edges) if edges else "overall consistency"
    return f"{leader} edges {trailer} on {edge_text} this season."


def compare_teams(request: CompareRequest) -> CompareResponse:
    team_a = normalize_team_name(request.team_a)
    team_b = normalize_team_name(request.team_b)

    if team_a is None:
        raise HTTPException(status_code=404, detail=f"Team not found: {request.team_a}")
    if team_b is None:
        raise HTTPException(status_code=404, detail=f"Team not found: {request.team_b}")
    if team_a == team_b:
        raise HTTPException(status_code=422, detail="Teams must be different")

    season = request.season or get_latest_season()
    matches = load_matches()

    available_seasons = set(matches["season"].unique())
    if season not in available_seasons:
        raise HTTPException(status_code=404, detail=f"Season not found: {season}")

    stats_a = get_team_season_stats(matches, team_a, season)
    stats_b = get_team_season_stats(matches, team_b, season)

    score_a = _comparison_score(stats_a)
    score_b = _comparison_score(stats_b)

    if abs(score_a - score_b) < 0.05:
        better = "even"
    elif score_a > score_b:
        better = "team_a"
    else:
        better = "team_b"

    return CompareResponse(
        team_a=team_a,
        team_b=team_b,
        season=season,
        team_a_stats=TeamStats(**stats_a),
        team_b_stats=TeamStats(**stats_b),
        better_team=better,
        summary=_build_comparison_summary(team_a, team_b, stats_a, stats_b, better),
    )
