from pydantic import BaseModel


class Team(BaseModel):
    name: str


class TeamsResponse(BaseModel):
    teams: list[Team]


class TeamFormResponse(BaseModel):
    team: str
    last_5_results: list[str]  # "W" | "D" | "L"
    points_last_5: int
    goals_for_last_5: int
    goals_against_last_5: int
