"use server";

import { chat, compareTeams, fetchTeamForm, predictMatch } from "@/lib/api";

function toActionError(error) {
  return { error: error.message || "Something went wrong" };
}

export async function fetchTeamFormAction(teamName) {
  if (!teamName?.trim()) {
    return { error: "Please select a team" };
  }

  try {
    const data = await fetchTeamForm(teamName);
    return { data };
  } catch (error) {
    return toActionError(error);
  }
}

export async function predictMatchAction({ home_team, away_team }) {
  if (!home_team || !away_team) {
    return { error: "Please select both teams" };
  }

  if (home_team === away_team) {
    return { error: "Home and away teams must be different" };
  }

  try {
    const data = await predictMatch(home_team, away_team);
    return { data };
  } catch (error) {
    return toActionError(error);
  }
}

export async function compareTeamsAction({ team_a, team_b, season }) {
  if (!team_a || !team_b) {
    return { error: "Please select both teams" };
  }

  if (team_a === team_b) {
    return { error: "Teams must be different" };
  }

  try {
    const data = await compareTeams(team_a, team_b, season);
    return { data };
  } catch (error) {
    return toActionError(error);
  }
}

export async function chatAction({ message, conversation_id }) {
  const trimmed = message?.trim();
  if (!trimmed) {
    return { error: "Please enter a question" };
  }

  try {
    const data = await chat(trimmed, conversation_id || undefined);
    return { data };
  } catch (error) {
    return toActionError(error);
  }
}
