from pydantic import BaseModel


class Team(BaseModel):
    name: str


class TeamsResponse(BaseModel):
    teams: list[Team]


class MatchResult(BaseModel):
    opponent: str
    home: bool
    goals_for: int
    goals_against: int
    result: str  # "W" | "D" | "L"


class TeamFormResponse(BaseModel):
    team_name: str
    matches: list[MatchResult]
