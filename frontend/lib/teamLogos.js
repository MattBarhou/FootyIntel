/**
 * Maps canonical API team names (CSV HomeTeam/AwayTeam spellings) to logo paths.
 */
export const TEAM_LOGO_MAP = {
  Arsenal: "/teams/arsenal.png",
  "Aston Villa": "/teams/aston_villa.png",
  Bournemouth: "/teams/bournemouth.png",
  Brentford: "/teams/brentford.png",
  Brighton: "/teams/brighton.png",
  Burnley: "/teams/burnley.png",
  Cardiff: "/teams/cardiff.png",
  Chelsea: "/teams/chelsea.png",
  "Crystal Palace": "/teams/palace.png",
  Everton: "/teams/everton.png",
  Fulham: "/teams/fulham.png",
  Huddersfield: "/teams/huddersfield.png",
  Ipswich: "/teams/ipswich.png",
  Leeds: "/teams/leeds.png",
  Leicester: "/teams/leicester.png",
  Liverpool: "/teams/liverpool.png",
  Luton: "/teams/luton.png",
  "Man City": "/teams/mancity.png",
  "Man United": "/teams/manunited.png",
  Newcastle: "/teams/newcastle.png",
  Norwich: "/teams/norwich.png",
  "Nott'm Forest": "/teams/nottingham.png",
  "Sheffield United": "/teams/sheffield.png",
  Southampton: "/teams/southampton.png",
  Stoke: "/teams/stoke.png",
  Sunderland: "/teams/sunderland.png",
  Swansea: "/teams/swansea.png",
  Tottenham: "/teams/spurs.png",
  Watford: "/teams/watford.png",
  "West Ham": "/teams/westham.png",
  Wolves: "/teams/wolves.png",
  "West Brom": "/teams/west_brom.png",
};

export function getTeamLogoSrc(teamName) {
  if (!teamName) {
    return null;
  }
  return TEAM_LOGO_MAP[teamName] ?? null;
}

export function getUnmappedTeams(teamNames) {
  return teamNames.filter((name) => !TEAM_LOGO_MAP[name]);
}
