from pydantic import BaseModel


class CompareRequest(BaseModel):
    team_a: str
    team_b: str
    season: str | None = None


class TeamStats(BaseModel):
    matches_played: int
    points: int
    ppg: float
    goals_for: float
    goals_against: float
    goal_diff: float
    shots: float
    shots_on_target: float
    corners: float
    cards: float
    win_rate: float


class CompareResponse(BaseModel):
    team_a: str
    team_b: str
    season: str
    team_a_stats: TeamStats
    team_b_stats: TeamStats
    better_team: str  # "team_a" | "team_b" | "even"
    summary: str
