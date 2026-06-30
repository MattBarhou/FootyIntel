from fastapi import APIRouter

from app.ml.data_loader import get_all_teams
from app.schemas.teams import Team, TeamFormResponse, TeamsResponse
from app.services.team_service import get_team_form

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=TeamsResponse)
async def list_teams() -> TeamsResponse:
    """Return all teams available in the dataset."""
    teams = [Team(name=name) for name in get_all_teams()]
    return TeamsResponse(teams=teams)


@router.get("/{team_name}/form", response_model=TeamFormResponse)
async def get_team_form_endpoint(team_name: str) -> TeamFormResponse:
    """Return recent match results and form for a team."""
    return get_team_form(team_name)
