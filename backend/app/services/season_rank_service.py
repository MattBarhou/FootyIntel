from __future__ import annotations

from app.ml.data_loader import load_matches
from app.ml.features import get_team_season_stats
from app.services.query_parser import expand_season_label, recent_season_labels


def _stem_for_label(season_label: str) -> str | None:
    matches = load_matches()
    for stem in matches["season"].unique():
        if expand_season_label(str(stem)) == season_label:
            return str(stem)
    return None


def rank_team_seasons(
    team: str,
    *,
    mode: str = "worst",
    years: int | None = 5,
) -> dict:
    """Rank a team's seasons by points (then goal difference, then wins)."""
    matches = load_matches()
    window = years or 5
    season_labels = recent_season_labels(window)

    ranked: list[dict] = []
    for label in season_labels:
        stem = _stem_for_label(label)
        if stem is None:
            continue
        stats = get_team_season_stats(matches, team, season=stem)
        if not stats["matches_played"]:
            continue

        wins = round(stats["win_rate"] * stats["matches_played"])
        ranked.append(
            {
                "season": label,
                "matches_played": int(stats["matches_played"]),
                "points": int(stats["points"]),
                "ppg": round(float(stats["ppg"]), 3),
                "win_rate": round(float(stats["win_rate"]), 3),
                "goals_for_avg": round(float(stats["goals_for"]), 3),
                "goals_against_avg": round(float(stats["goals_against"]), 3),
                "goal_diff_avg": round(float(stats["goal_diff"]), 3),
                "wins": int(wins),
            }
        )

    ranked.sort(
        key=lambda row: (row["points"], row["goal_diff_avg"], row["wins"], row["ppg"]),
        reverse=(mode == "best"),
    )

    return {
        "team": team,
        "mode": mode,
        "years": window,
        "seasons_considered": [row["season"] for row in ranked],
        "ranking": ranked,
        "selected": ranked[0] if ranked else None,
    }


def format_season_rank_context(result: dict) -> str:
    if not result["selected"]:
        return (
            f"No season stats were available for {result['team']} "
            f"in the last {result['years']} seasons."
        )

    selected = result["selected"]
    mode_word = "best" if result["mode"] == "best" else "worst"
    lines = [
        "Season Rank Tool Result:",
        (
            f"{result['team']}'s {mode_word} Premier League season in the last "
            f"{result['years']} seasons is {selected['season']}."
        ),
        (
            f"In {selected['season']} they played {selected['matches_played']} matches, "
            f"earned {selected['points']} points ({selected['ppg']:.2f} PPG), "
            f"with a win rate of {selected['win_rate'] * 100:.1f}%."
        ),
        (
            f"Average goals for/against per match: "
            f"{selected['goals_for_avg']:.2f} / {selected['goals_against_avg']:.2f} "
            f"(GD {selected['goal_diff_avg']:+.2f})."
        ),
        "Seasons ranked by points (then goal difference):",
    ]

    ordered = sorted(
        result["ranking"],
        key=lambda row: (row["points"], row["goal_diff_avg"], row["wins"]),
        reverse=True,
    )
    for index, row in enumerate(ordered, start=1):
        marker = " <- selected" if row["season"] == selected["season"] else ""
        lines.append(
            f"{index}. {row['season']}: {row['points']} pts, "
            f"{row['ppg']:.2f} PPG, GD {row['goal_diff_avg']:+.2f}{marker}"
        )

    return "\n".join(lines)
