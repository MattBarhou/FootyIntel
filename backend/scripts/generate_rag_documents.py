"""Generate template-based RAG text documents from Premier League CSV data."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

RAW_DIR = BACKEND_DIR / "data" / "raw"
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"

KEEP_COLUMNS = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTR",
    "FTHG",
    "FTAG",
    "HS",
    "HST",
    "HC",
    "AS",
    "AST",
    "AC",
]

NUMERIC_COLUMNS = ["FTHG", "FTAG", "HS", "HST", "HC", "AS", "AST", "AC"]


def expand_season(season: str) -> str:
    """Convert filename season stem like '23-24' to '2023-24'."""
    parts = str(season).split("-")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return str(season)
    start = int(parts[0])
    end = int(parts[1])
    century = 2000 if start < 100 else 0
    return f"{century + start}-{end:02d}" if end < 100 else f"{century + start}-{end}"


def slugify(value: str) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def _safe_int(value) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _result_for_team(ftr: str, is_home: bool) -> str:
    if ftr == "D":
        return "D"
    if ftr == "H":
        return "W" if is_home else "L"
    if ftr == "A":
        return "L" if is_home else "W"
    return "D"


def load_csv_files(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Load every CSV in raw_dir into one cleaned dataframe."""
    csv_paths = sorted(raw_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    frames: list[pd.DataFrame] = []
    for csv_path in csv_paths:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        available = [col for col in KEEP_COLUMNS if col in df.columns]
        season_df = df[available].copy()
        season_df["season"] = csv_path.stem
        frames.append(season_df)

    matches = pd.concat(frames, ignore_index=True)
    matches["Date"] = pd.to_datetime(matches["Date"], dayfirst=True, errors="coerce")
    matches["HomeTeam"] = matches["HomeTeam"].astype(str).str.strip()
    matches["AwayTeam"] = matches["AwayTeam"].astype(str).str.strip()
    matches = matches.dropna(subset=["Date", "HomeTeam", "AwayTeam", "FTR"])
    matches = matches.sort_values("Date").reset_index(drop=True)

    for col in NUMERIC_COLUMNS:
        if col in matches.columns:
            matches[col] = pd.to_numeric(matches[col], errors="coerce")

    print(f"Loaded {len(csv_paths)} CSV files ({len(matches)} matches).")
    return matches


def create_match_summary(row: pd.Series) -> dict:
    """Build one RAG document for a single match."""
    home = str(row["HomeTeam"])
    away = str(row["AwayTeam"])
    season_key = str(row["season"])
    season_label = expand_season(season_key)
    match_date = pd.Timestamp(row["Date"]).strftime("%Y-%m-%d")
    home_goals = _safe_int(row.get("FTHG"))
    away_goals = _safe_int(row.get("FTAG"))
    ftr = str(row["FTR"]).strip().upper()

    lines = [
        "Match Summary:",
        f"{home} played {away} on {match_date} in the {season_label} Premier League season.",
    ]

    if home_goals is not None and away_goals is not None:
        lines.append(f"Final score: {home} {home_goals} - {away_goals} {away}.")

    if ftr == "H":
        lines.append(f"Result: {home} won at home.")
    elif ftr == "A":
        lines.append(f"Result: {away} won away.")
    elif ftr == "D":
        lines.append("Result: The match ended in a draw.")

    home_shots = _safe_int(row.get("HS"))
    home_sot = _safe_int(row.get("HST"))
    home_corners = _safe_int(row.get("HC"))
    if home_shots is not None and home_sot is not None and home_corners is not None:
        lines.append(
            f"{home} had {home_shots} shots, {home_sot} shots on target, "
            f"and {home_corners} corners."
        )

    away_shots = _safe_int(row.get("AS"))
    away_sot = _safe_int(row.get("AST"))
    away_corners = _safe_int(row.get("AC"))
    if away_shots is not None and away_sot is not None and away_corners is not None:
        lines.append(
            f"{away} had {away_shots} shots, {away_sot} shots on target, "
            f"and {away_corners} corners."
        )

    doc_id = (
        f"match_{slugify(season_key)}_{pd.Timestamp(row['Date']).strftime('%Y%m%d')}"
        f"_{slugify(home)}_{slugify(away)}"
    )

    return {
        "id": doc_id,
        "text": "\n".join(lines),
        "metadata": {
            "type": "match_summary",
            "season": season_label,
            "home_team": home,
            "away_team": away,
            "date": match_date,
        },
    }


def _team_season_matches(df: pd.DataFrame, season: str, team: str) -> pd.DataFrame:
    season_df = df[df["season"] == season]
    mask = (season_df["HomeTeam"] == team) | (season_df["AwayTeam"] == team)
    return season_df.loc[mask].sort_values("Date")


def _aggregate_team_matches(team_matches: pd.DataFrame, team: str) -> dict:
    wins = draws = losses = 0
    goals_for = goals_against = 0
    shots_on_target: list[float] = []

    for _, row in team_matches.iterrows():
        is_home = row["HomeTeam"] == team
        result = _result_for_team(str(row["FTR"]).strip().upper(), is_home)
        if result == "W":
            wins += 1
        elif result == "D":
            draws += 1
        else:
            losses += 1

        gf = _safe_int(row["FTHG"] if is_home else row["FTAG"])
        ga = _safe_int(row["FTAG"] if is_home else row["FTHG"])
        if gf is not None:
            goals_for += gf
        if ga is not None:
            goals_against += ga

        sot_col = "HST" if is_home else "AST"
        if sot_col in row.index:
            sot = row[sot_col]
            if pd.notna(sot):
                shots_on_target.append(float(sot))

    return {
        "matches": len(team_matches),
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "avg_sot": (
            sum(shots_on_target) / len(shots_on_target) if shots_on_target else None
        ),
    }


def create_team_form_summaries(df: pd.DataFrame, n: int = 5) -> list[dict]:
    """Generate last-N-match form summaries for each team in each season."""
    documents: list[dict] = []
    seasons = sorted(df["season"].unique())

    for season in seasons:
        season_df = df[df["season"] == season]
        teams = sorted(
            pd.unique(
                pd.concat([season_df["HomeTeam"], season_df["AwayTeam"]], ignore_index=True)
            )
        )
        season_label = expand_season(str(season))

        for team in teams:
            team_matches = _team_season_matches(df, str(season), team)
            if team_matches.empty:
                continue

            recent = team_matches.tail(n)
            stats = _aggregate_team_matches(recent, team)

            lines = [
                "Team Form Summary:",
                (
                    f"{team}'s last {stats['matches']} matches in the {season_label} "
                    f"Premier League season included {stats['wins']} wins, "
                    f"{stats['draws']} draws, and {stats['losses']} losses."
                ),
                (
                    f"They scored {stats['goals_for']} goals and conceded "
                    f"{stats['goals_against']} goals."
                ),
            ]
            if stats["avg_sot"] is not None:
                lines.append(
                    f"They averaged {stats['avg_sot']:.1f} shots on target per match."
                )

            documents.append(
                {
                    "id": f"form_{slugify(str(season))}_{slugify(team)}",
                    "text": "\n".join(lines),
                    "metadata": {
                        "type": "team_form",
                        "season": season_label,
                        "team": team,
                    },
                }
            )

    return documents


def create_season_summaries(df: pd.DataFrame) -> list[dict]:
    """Generate full-season performance summaries for each team."""
    documents: list[dict] = []
    seasons = sorted(df["season"].unique())

    for season in seasons:
        season_df = df[df["season"] == season]
        teams = sorted(
            pd.unique(
                pd.concat([season_df["HomeTeam"], season_df["AwayTeam"]], ignore_index=True)
            )
        )
        season_label = expand_season(str(season))

        for team in teams:
            team_matches = _team_season_matches(df, str(season), team)
            if team_matches.empty:
                continue

            stats = _aggregate_team_matches(team_matches, team)
            avg_goals = (
                stats["goals_for"] / stats["matches"] if stats["matches"] else 0.0
            )

            lines = [
                "Season Summary:",
                (
                    f"{team} in the {season_label} Premier League season played "
                    f"{stats['matches']} matches."
                ),
                (
                    f"They had {stats['wins']} wins, {stats['draws']} draws, "
                    f"and {stats['losses']} losses."
                ),
                (
                    f"They scored {stats['goals_for']} goals and conceded "
                    f"{stats['goals_against']} goals."
                ),
                f"Their average goals per match was {avg_goals:.2f}.",
            ]

            documents.append(
                {
                    "id": f"season_{slugify(str(season))}_{slugify(team)}",
                    "text": "\n".join(lines),
                    "metadata": {
                        "type": "season_summary",
                        "season": season_label,
                        "team": team,
                    },
                }
            )

    return documents


def create_home_away_summaries(df: pd.DataFrame) -> list[dict]:
    """Generate home vs away performance summaries for each team and season."""
    documents: list[dict] = []
    seasons = sorted(df["season"].unique())

    for season in seasons:
        season_df = df[df["season"] == season]
        teams = sorted(
            pd.unique(
                pd.concat([season_df["HomeTeam"], season_df["AwayTeam"]], ignore_index=True)
            )
        )
        season_label = expand_season(str(season))

        for team in teams:
            team_matches = _team_season_matches(df, str(season), team)
            if team_matches.empty:
                continue

            home_matches = team_matches[team_matches["HomeTeam"] == team]
            away_matches = team_matches[team_matches["AwayTeam"] == team]
            home_stats = _aggregate_team_matches(home_matches, team)
            away_stats = _aggregate_team_matches(away_matches, team)

            lines = [
                "Home/Away Summary:",
                f"{team} home and away split in the {season_label} Premier League season.",
            ]
            if home_stats["matches"]:
                lines.append(
                    (
                        f"At home they played {home_stats['matches']} matches with "
                        f"{home_stats['wins']} wins, {home_stats['draws']} draws, "
                        f"and {home_stats['losses']} losses, scoring {home_stats['goals_for']} "
                        f"and conceding {home_stats['goals_against']}."
                    )
                )
            if away_stats["matches"]:
                lines.append(
                    (
                        f"Away from home they played {away_stats['matches']} matches with "
                        f"{away_stats['wins']} wins, {away_stats['draws']} draws, "
                        f"and {away_stats['losses']} losses, scoring {away_stats['goals_for']} "
                        f"and conceding {away_stats['goals_against']}."
                    )
                )

            documents.append(
                {
                    "id": f"homeaway_{slugify(str(season))}_{slugify(team)}",
                    "text": "\n".join(lines),
                    "metadata": {
                        "type": "home_away_summary",
                        "season": season_label,
                        "team": team,
                    },
                }
            )

    return documents


def create_h2h_summaries(df: pd.DataFrame, min_meetings: int = 2) -> list[dict]:
    """Generate head-to-head summaries for team pairs with enough meetings."""
    documents: list[dict] = []
    working = df.copy()
    working["pair_a"] = working[["HomeTeam", "AwayTeam"]].min(axis=1)
    working["pair_b"] = working[["HomeTeam", "AwayTeam"]].max(axis=1)

    for (team_a, team_b), meetings in working.groupby(["pair_a", "pair_b"], sort=True):
        meetings = meetings.sort_values("Date")
        if len(meetings) < min_meetings:
            continue

        a_wins = b_wins = draws = 0
        a_goals = b_goals = 0
        recent_lines: list[str] = []

        for _, row in meetings.iterrows():
            home = str(row["HomeTeam"])
            away = str(row["AwayTeam"])
            ftr = str(row["FTR"]).strip().upper()
            hg = _safe_int(row.get("FTHG")) or 0
            ag = _safe_int(row.get("FTAG")) or 0

            if home == team_a:
                a_goals += hg
                b_goals += ag
            else:
                a_goals += ag
                b_goals += hg

            if ftr == "D":
                draws += 1
                winner = "draw"
            elif ftr == "H":
                if home == team_a:
                    a_wins += 1
                    winner = team_a
                else:
                    b_wins += 1
                    winner = team_b
            else:
                if away == team_a:
                    a_wins += 1
                    winner = team_a
                else:
                    b_wins += 1
                    winner = team_b

            match_date = pd.Timestamp(row["Date"]).strftime("%Y-%m-%d")
            season_label = expand_season(str(row["season"]))
            recent_lines.append(
                f"{match_date} ({season_label}): {home} {hg}-{ag} {away}"
                + (f" ({winner} won)" if winner != "draw" else " (draw)")
            )

        lines = [
            "Head-to-Head Summary:",
            f"{team_a} vs {team_b} across Premier League meetings in the dataset.",
            (
                f"They played {len(meetings)} matches. {team_a} won {a_wins}, "
                f"{team_b} won {b_wins}, and {draws} ended in draws."
            ),
            f"Goals scored: {team_a} {a_goals}, {team_b} {b_goals}.",
            "Recent meetings:",
            *recent_lines[-5:],
        ]

        documents.append(
            {
                "id": f"h2h_{slugify(team_a)}_{slugify(team_b)}",
                "text": "\n".join(lines),
                "metadata": {
                    "type": "h2h_summary",
                    "team_a": team_a,
                    "team_b": team_b,
                    "team": team_a,
                    "opponent": team_b,
                },
            }
        )

    return documents


def save_documents(documents: list[dict], processed_dir: Path = PROCESSED_DIR) -> None:
    """Write documents to JSON and a flattened CSV for inspection."""
    processed_dir.mkdir(parents=True, exist_ok=True)

    json_path = processed_dir / "rag_documents.json"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(documents, handle, indent=2, ensure_ascii=False)

    rows = []
    for doc in documents:
        meta = doc.get("metadata", {})
        rows.append(
            {
                "id": doc["id"],
                "text": doc["text"],
                "type": meta.get("type", ""),
                "season": meta.get("season", ""),
                "team": meta.get("team", ""),
                "opponent": meta.get("opponent", ""),
                "home_team": meta.get("home_team", ""),
                "away_team": meta.get("away_team", ""),
                "team_a": meta.get("team_a", ""),
                "team_b": meta.get("team_b", ""),
                "date": meta.get("date", ""),
            }
        )

    csv_path = processed_dir / "rag_documents.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    print(f"Saved {len(documents)} documents to:")
    print(f"  {json_path}")
    print(f"  {csv_path}")


def main() -> None:
    matches = load_csv_files(RAW_DIR)

    match_docs = [create_match_summary(row) for _, row in matches.iterrows()]
    form_docs = create_team_form_summaries(matches)
    season_docs = create_season_summaries(matches)
    home_away_docs = create_home_away_summaries(matches)
    h2h_docs = create_h2h_summaries(matches)

    documents = match_docs + form_docs + season_docs + home_away_docs + h2h_docs
    save_documents(documents, PROCESSED_DIR)

    print(
        f"Created {len(match_docs)} match summaries, "
        f"{len(form_docs)} team form summaries, "
        f"{len(season_docs)} season summaries, "
        f"{len(home_away_docs)} home/away summaries, "
        f"{len(h2h_docs)} H2H summaries "
        f"({len(documents)} total)."
    )


if __name__ == "__main__":
    main()
