from fastapi import HTTPException

from app.ml.data_loader import normalize_team_name
from app.ml.features import get_recent_team_form
from app.schemas.teams import TeamFormResponse


def get_team_form(team_name: str) -> TeamFormResponse:
    team = normalize_team_name(team_name)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team not found: {team_name}")

    form = get_recent_team_form(team)
    return TeamFormResponse(team=team, **form)
