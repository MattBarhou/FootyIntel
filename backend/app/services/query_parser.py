from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.ml.data_loader import get_all_teams, load_matches

TEAM_ALIASES = {
    "manchester city": "Man City",
    "man city": "Man City",
    "manchester united": "Man United",
    "man united": "Man United",
    "man utd": "Man United",
    "spurs": "Tottenham",
    "tottenham hotspur": "Tottenham",
    "nottingham forest": "Nott'm Forest",
    "nottm forest": "Nott'm Forest",
    "wolverhampton": "Wolves",
    "wolverhampton wanderers": "Wolves",
    "brighton and hove albion": "Brighton",
    "brighton & hove albion": "Brighton",
    "newcastle united": "Newcastle",
    "west ham united": "West Ham",
    "west bromwich albion": "West Brom",
    "sheffield utd": "Sheffield United",
    "sheff utd": "Sheffield United",
    "nottingham": "Nott'm Forest",
}


@dataclass
class ParsedQuery:
    teams: list[str] = field(default_factory=list)
    seasons: list[str] = field(default_factory=list)
    intent: str = "general"
    rank_mode: str | None = None  # "best" | "worst"
    years: int | None = None
    prefers_home_away: bool = False
    prefers_h2h: bool = False
    prefers_form: bool = False
    prefers_season: bool = False


def expand_season_label(season: str) -> str:
    """Convert filename season stem like '23-24' to '2023-24'."""
    parts = str(season).split("-")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return str(season)
    start = int(parts[0])
    end = int(parts[1])
    century = 2000 if start < 100 else 0
    return f"{century + start}-{end:02d}" if end < 100 else f"{century + start}-{end}"


def season_sort_key(season_label: str) -> tuple[int, int]:
    parts = str(season_label).split("-")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return int(parts[0]), int(parts[1])
    return (0, 0)


def _canonical_team(name: str) -> str | None:
    lowered = name.strip().lower()
    if lowered in TEAM_ALIASES:
        alias_target = TEAM_ALIASES[lowered]
        teams = set(get_all_teams())
        return alias_target if alias_target in teams else None

    lookup = {team.lower(): team for team in get_all_teams()}
    return lookup.get(lowered)


def extract_teams(message: str, limit: int = 2) -> list[str]:
    text = message.lower()
    found: list[tuple[int, str]] = []

    alias_names = sorted(TEAM_ALIASES.keys(), key=len, reverse=True)
    for alias in alias_names:
        pattern = rf"\b{re.escape(alias)}\b"
        for match in re.finditer(pattern, text):
            canonical = _canonical_team(alias)
            if canonical:
                found.append((match.start(), canonical))

    for team in sorted(get_all_teams(), key=len, reverse=True):
        pattern = rf"\b{re.escape(team.lower())}\b"
        for match in re.finditer(pattern, text):
            found.append((match.start(), team))

    ordered: list[str] = []
    seen: set[str] = set()
    for _, team in sorted(found, key=lambda item: item[0]):
        if team not in seen:
            ordered.append(team)
            seen.add(team)
        if len(ordered) >= limit:
            break
    return ordered


def extract_seasons(message: str) -> list[str]:
    text = message.lower()
    seasons: list[str] = []

    patterns = [
        r"\b(20\d{2})\s*[-/–]\s*(\d{2})\b",
        r"\b(\d{2})\s*[-/–]\s*(\d{2})\b",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            start, end = match.group(1), match.group(2)
            if len(start) == 4:
                label = f"{start}-{end}"
            else:
                label = expand_season_label(f"{start}-{end}")
            if label not in seasons:
                seasons.append(label)

    return seasons


def extract_years_window(message: str) -> int | None:
    patterns = [
        r"\blast\s+(\d+)\s+years?\b",
        r"\bpast\s+(\d+)\s+years?\b",
        r"\blast\s+(\d+)\s+seasons?\b",
        r"\bpast\s+(\d+)\s+seasons?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            value = int(match.group(1))
            if 1 <= value <= 20:
                return value
    return None


def parse_query(message: str) -> ParsedQuery:
    text = message.lower()
    teams = extract_teams(message)
    seasons = extract_seasons(message)
    years = extract_years_window(message)

    prefers_h2h = bool(
        re.search(r"\b(versus|against|head[-\s]?to[-\s]?head|h2h)\b", text)
        or (
            re.search(r"\bvs\.?\b", text)
            and not re.search(r"\bhome\b.*\bvs\.?\b.*\baway\b", text)
        )
    ) or len(teams) >= 2
    prefers_home_away = bool(
        re.search(r"\b(home|away)\b", text)
        or re.search(r"\bhome\b.*\bvs\.?\b.*\baway\b", text)
    )
    prefers_form = bool(re.search(r"\b(form|last\s+5|recent)\b", text))
    prefers_season = bool(
        seasons
        or re.search(r"\b(season|campaign|table|points|record)\b", text)
    )

    rank_mode = None
    if re.search(r"\b(worst|lowest|poorest|least\s+successful)\b", text):
        rank_mode = "worst"
    elif re.search(r"\b(best|highest|strongest|most\s+successful)\b", text):
        rank_mode = "best"

    intent = "general"
    if rank_mode and teams:
        intent = "season_rank"
    elif prefers_h2h and len(teams) >= 2:
        intent = "h2h"
    elif prefers_home_away and teams:
        intent = "home_away"
    elif prefers_form and teams:
        intent = "form"
    elif prefers_season and teams:
        intent = "season"

    return ParsedQuery(
        teams=teams,
        seasons=seasons,
        intent=intent,
        rank_mode=rank_mode,
        years=years,
        prefers_home_away=prefers_home_away,
        prefers_h2h=prefers_h2h,
        prefers_form=prefers_form,
        prefers_season=prefers_season,
    )


def recent_season_labels(n: int) -> list[str]:
    matches = load_matches()
    stems = sorted({str(season) for season in matches["season"].unique()})
    labels = [expand_season_label(stem) for stem in stems]
    labels = sorted(set(labels), key=season_sort_key)
    if n <= 0:
        return labels
    return labels[-n:]


def available_season_labels() -> list[str]:
    return recent_season_labels(0)
