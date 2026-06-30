from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

ROLLING_WINDOW = 5
H2H_WINDOW = 3

RESULT_TO_LABEL = {"H": 0, "D": 1, "A": 2}
LABEL_TO_RESULT = {v: k for k, v in RESULT_TO_LABEL.items()}


@dataclass
class TeamMatchRecord:
    date: pd.Timestamp
    season: str
    is_home: bool
    goals_for: int
    goals_against: int
    points: int
    shots: float
    shots_on_target: float
    corners: float
    yellow_cards: float
    red_cards: float


@dataclass
class MatchHistory:
    team_records: dict[str, list[TeamMatchRecord]] = field(
        default_factory=lambda: defaultdict(list)
    )
    h2h_records: dict[tuple[str, str], list[dict[str, Any]]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_match(self, row: pd.Series) -> None:
        home = row["HomeTeam"]
        away = row["AwayTeam"]
        date = row["Date"]
        season = row["season"]

        home_points = {"H": 3, "D": 1, "A": 0}[row["FTR"]]
        away_points = {"H": 0, "D": 1, "A": 3}[row["FTR"]]

        self.team_records[home].append(
            TeamMatchRecord(
                date=date,
                season=season,
                is_home=True,
                goals_for=int(row["FTHG"]),
                goals_against=int(row["FTAG"]),
                points=home_points,
                shots=float(row["HS"]),
                shots_on_target=float(row["HST"]),
                corners=float(row["HC"]),
                yellow_cards=float(row["HY"]),
                red_cards=float(row["HR"]),
            )
        )
        self.team_records[away].append(
            TeamMatchRecord(
                date=date,
                season=season,
                is_home=False,
                goals_for=int(row["FTAG"]),
                goals_against=int(row["FTHG"]),
                points=away_points,
                shots=float(row["AS"]),
                shots_on_target=float(row["AST"]),
                corners=float(row["AC"]),
                yellow_cards=float(row["AY"]),
                red_cards=float(row["AR"]),
            )
        )

        pair_key = tuple(sorted((home, away)))
        self.h2h_records[pair_key].append(
            {
                "date": date,
                "home": home,
                "away": away,
                "ftr": row["FTR"],
                "total_goals": int(row["FTHG"]) + int(row["FTAG"]),
            }
        )


def _filter_records(
    records: list[TeamMatchRecord],
    *,
    home_only: bool = False,
    away_only: bool = False,
    season: str | None = None,
) -> list[TeamMatchRecord]:
    filtered = records
    if home_only:
        filtered = [r for r in filtered if r.is_home]
    if away_only:
        filtered = [r for r in filtered if not r.is_home]
    if season is not None:
        filtered = [r for r in filtered if r.season == season]
    return filtered


def _rolling_team_features(
    records: list[TeamMatchRecord],
    window: int = ROLLING_WINDOW,
    *,
    home_only: bool = False,
    away_only: bool = False,
) -> dict[str, float]:
    recent = _filter_records(records, home_only=home_only, away_only=away_only)[-window:]
    if not recent:
        return {
            "ppg": np.nan,
            "goals_for": np.nan,
            "goals_against": np.nan,
            "goal_diff": np.nan,
            "wins": np.nan,
            "draws": np.nan,
            "losses": np.nan,
            "shots": np.nan,
            "shots_on_target": np.nan,
            "corners": np.nan,
            "cards": np.nan,
        }

    n = len(recent)
    goals_for = sum(r.goals_for for r in recent) / n
    goals_against = sum(r.goals_against for r in recent) / n
    wins = sum(1 for r in recent if r.points == 3) / n
    draws = sum(1 for r in recent if r.points == 1) / n
    losses = sum(1 for r in recent if r.points == 0) / n

    return {
        "ppg": sum(r.points for r in recent) / n,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goal_diff": goals_for - goals_against,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "shots": sum(r.shots for r in recent) / n,
        "shots_on_target": sum(r.shots_on_target for r in recent) / n,
        "corners": sum(r.corners for r in recent) / n,
        "cards": sum(r.yellow_cards + r.red_cards for r in recent) / n,
    }


def _prefix_features(features: dict[str, float], prefix: str) -> dict[str, float]:
    return {f"{prefix}_{key}": value for key, value in features.items()}


def _rest_days(records: list[TeamMatchRecord], current_date: pd.Timestamp) -> float:
    if not records:
        return np.nan
    last_date = records[-1].date
    return float((current_date - last_date).days)


def _season_matchday(records: list[TeamMatchRecord], season: str) -> float:
    count = sum(1 for r in records if r.season == season)
    return float(count + 1)


def _h2h_features(
    history: MatchHistory,
    home_team: str,
    away_team: str,
    window: int = H2H_WINDOW,
) -> dict[str, float]:
    pair_key = tuple(sorted((home_team, away_team)))
    meetings = [
        m
        for m in history.h2h_records[pair_key]
        if m["home"] == home_team and m["away"] == away_team
    ][-window:]

    if not meetings:
        return {
            "h2h_home_wins": np.nan,
            "h2h_draws": np.nan,
            "h2h_away_wins": np.nan,
            "h2h_avg_goals": np.nan,
        }

    n = len(meetings)
    home_wins = sum(1 for m in meetings if m["ftr"] == "H") / n
    draws = sum(1 for m in meetings if m["ftr"] == "D") / n
    away_wins = sum(1 for m in meetings if m["ftr"] == "A") / n
    avg_goals = sum(m["total_goals"] for m in meetings) / n

    return {
        "h2h_home_wins": home_wins,
        "h2h_draws": draws,
        "h2h_away_wins": away_wins,
        "h2h_avg_goals": avg_goals,
    }


def _odds_features(row: pd.Series) -> dict[str, float]:
    avg_h = row.get("AvgH", np.nan)
    avg_d = row.get("AvgD", np.nan)
    avg_a = row.get("AvgA", np.nan)

    features = {
        "odds_home": avg_h,
        "odds_draw": avg_d,
        "odds_away": avg_a,
    }

    if pd.notna(avg_h) and pd.notna(avg_d) and pd.notna(avg_a) and min(avg_h, avg_d, avg_a) > 0:
        raw = np.array([1 / avg_h, 1 / avg_d, 1 / avg_a])
        total = raw.sum()
        adjusted = raw / total
        features.update(
            {
                "implied_prob_home": float(adjusted[0]),
                "implied_prob_draw": float(adjusted[1]),
                "implied_prob_away": float(adjusted[2]),
            }
        )
        favorite_idx = int(np.argmin([avg_h, avg_d, avg_a]))
        features["odds_favorite"] = float(favorite_idx)
    else:
        features.update(
            {
                "implied_prob_home": np.nan,
                "implied_prob_draw": np.nan,
                "implied_prob_away": np.nan,
                "odds_favorite": np.nan,
            }
        )

    return features


def _build_fixture_row(
    history: MatchHistory,
    home_team: str,
    away_team: str,
    date: pd.Timestamp,
    season: str,
    odds_row: pd.Series | None = None,
) -> dict[str, float]:
    home_records = history.team_records[home_team]
    away_records = history.team_records[away_team]

    features: dict[str, float] = {}
    features.update(_prefix_features(_rolling_team_features(home_records), "home"))
    features.update(_prefix_features(_rolling_team_features(home_records, home_only=True), "home_home"))
    features.update(_prefix_features(_rolling_team_features(away_records), "away"))
    features.update(_prefix_features(_rolling_team_features(away_records, away_only=True), "away_away"))
    features.update(_h2h_features(history, home_team, away_team))
    features["home_rest_days"] = _rest_days(home_records, date)
    features["away_rest_days"] = _rest_days(away_records, date)
    features["home_matchday"] = _season_matchday(home_records, season)
    features["away_matchday"] = _season_matchday(away_records, season)

    if odds_row is not None:
        features.update(_odds_features(odds_row))
    else:
        features.update(_odds_features(pd.Series(dtype=float)))

    return features


def get_feature_columns() -> list[str]:
    sample = _build_fixture_row(
        MatchHistory(),
        "Arsenal",
        "Chelsea",
        pd.Timestamp("2024-01-01"),
        "23-24",
    )
    return list(sample.keys())


def build_feature_matrix(matches: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Build leakage-safe features for all completed matches."""
    history = MatchHistory()
    rows: list[dict[str, float]] = []
    labels: list[int] = []

    for _, row in matches.iterrows():
        feature_row = _build_fixture_row(
            history,
            row["HomeTeam"],
            row["AwayTeam"],
            row["Date"],
            row["season"],
            odds_row=row,
        )
        rows.append(feature_row)
        labels.append(RESULT_TO_LABEL[row["FTR"]])
        history.add_match(row)

    X = pd.DataFrame(rows)
    y = pd.Series(labels, name="result")
    return X, y


def build_inference_features(
    matches: pd.DataFrame,
    home_team: str,
    away_team: str,
) -> pd.DataFrame:
    """Build a single feature row for a hypothetical upcoming fixture."""
    history = MatchHistory()
    for _, row in matches.iterrows():
        history.add_match(row)

    latest = matches.iloc[-1]
    season = str(latest["season"])
    inference_date = latest["Date"] + pd.Timedelta(days=1)

    feature_row = _build_fixture_row(
        history,
        home_team,
        away_team,
        inference_date,
        season,
        odds_row=None,
    )
    return pd.DataFrame([feature_row])


def get_team_season_stats(
    matches: pd.DataFrame,
    team: str,
    season: str | None = None,
    window: int = ROLLING_WINDOW,
) -> dict[str, float]:
    """Aggregate team performance stats for comparison."""
    if season is None:
        season = str(matches["season"].iloc[-1])

    season_matches = matches[matches["season"] == season].sort_values("Date")
    history = MatchHistory()
    for _, row in season_matches.iterrows():
        history.add_match(row)

    records = [r for r in history.team_records[team] if r.season == season]
    if not records:
        return {
            "matches_played": 0,
            "points": 0,
            "ppg": 0.0,
            "goals_for": 0.0,
            "goals_against": 0.0,
            "goal_diff": 0.0,
            "shots": 0.0,
            "shots_on_target": 0.0,
            "corners": 0.0,
            "cards": 0.0,
            "win_rate": 0.0,
        }

    n = len(records)
    points = sum(r.points for r in records)
    goals_for = sum(r.goals_for for r in records)
    goals_against = sum(r.goals_against for r in records)
    wins = sum(1 for r in records if r.points == 3)

    recent = _rolling_team_features(records, window=min(window, n))

    return {
        "matches_played": n,
        "points": points,
        "ppg": points / n,
        "goals_for": goals_for / n,
        "goals_against": goals_against / n,
        "goal_diff": (goals_for - goals_against) / n,
        "shots": recent["shots"],
        "shots_on_target": recent["shots_on_target"],
        "corners": recent["corners"],
        "cards": recent["cards"],
        "win_rate": wins / n,
    }
