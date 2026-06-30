from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

CORE_COLUMNS = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTR",
    "FTHG",
    "FTAG",
    "HS",
    "HST",
    "HC",
    "HY",
    "HR",
    "AS",
    "AST",
    "AC",
    "AY",
    "AR",
    "AvgH",
    "AvgD",
    "AvgA",
]


def _season_from_filename(path: Path) -> str:
    return path.stem


@lru_cache(maxsize=1)
def load_matches() -> pd.DataFrame:
    """Load and concatenate all season CSVs, sorted chronologically."""
    frames: list[pd.DataFrame] = []

    for csv_path in sorted(RAW_DATA_DIR.glob("*.csv")):
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        available = [col for col in CORE_COLUMNS if col in df.columns]
        season_df = df[available].copy()
        season_df["season"] = _season_from_filename(csv_path)
        frames.append(season_df)

    matches = pd.concat(frames, ignore_index=True)
    matches["Date"] = pd.to_datetime(matches["Date"], dayfirst=True, errors="coerce")
    matches = matches.dropna(subset=["Date", "HomeTeam", "AwayTeam", "FTR"])
    matches = matches.sort_values("Date").reset_index(drop=True)

    for col in ["FTHG", "FTAG", "HS", "HST", "HC", "HY", "HR", "AS", "AST", "AC", "AY", "AR"]:
        if col in matches.columns:
            matches[col] = pd.to_numeric(matches[col], errors="coerce")

    for col in ["AvgH", "AvgD", "AvgA"]:
        if col in matches.columns:
            matches[col] = pd.to_numeric(matches[col], errors="coerce")

    return matches


@lru_cache(maxsize=1)
def get_all_teams() -> tuple[str, ...]:
    matches = load_matches()
    teams = pd.unique(pd.concat([matches["HomeTeam"], matches["AwayTeam"]], ignore_index=True))
    return tuple(sorted(teams))


def normalize_team_name(name: str) -> str | None:
    """Resolve user input to canonical team name (case-insensitive)."""
    lookup = {team.lower(): team for team in get_all_teams()}
    return lookup.get(name.strip().lower())


def get_latest_season() -> str:
    matches = load_matches()
    return str(matches["season"].iloc[-1])
