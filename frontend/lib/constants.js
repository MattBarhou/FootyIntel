export const FORM_RESULT_STYLES = {
  W: { label: "Win", className: "result-bauhaus-win" },
  D: { label: "Draw", className: "result-bauhaus-draw" },
  L: { label: "Loss", className: "result-bauhaus-loss" },
};

export const PREDICTED_RESULT_LABELS = {
  H: "Home Win",
  D: "Draw",
  A: "Away Win",
};

export const COMPARE_STAT_LABELS = {
  matches_played: "Matches Played",
  points: "Points",
  ppg: "Points per Game",
  goals_for: "Goals For (avg)",
  goals_against: "Goals Against (avg)",
  goal_diff: "Goal Difference",
  shots: "Shots (avg)",
  shots_on_target: "Shots on Target (avg)",
  corners: "Corners (avg)",
  cards: "Cards (avg)",
  win_rate: "Win Rate",
};

export const BETTER_TEAM_LABELS = {
  team_a: "Team A",
  team_b: "Team B",
  even: "Even",
};

export function getTeamInitials(name) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}
