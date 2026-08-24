import { cache } from "react";

function getApiUrl() {
  const url = process.env.API_URL;
  if (!url) {
    throw new Error("API_URL environment variable is not set");
  }
  return url.replace(/\/$/, "");
}

async function parseErrorResponse(response) {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body.detail)) {
      return body.detail.map((item) => item.msg).join(", ");
    }
  } catch {
    // fall through
  }
  return `Request failed with status ${response.status}`;
}

async function apiFetch(path, options = {}) {
  const response = await fetch(`${getApiUrl()}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const message = await parseErrorResponse(response);
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return response.json();
}

export const getTeams = cache(async () => {
  return apiFetch("/api/teams", {
    next: { revalidate: 86400 },
  });
});

export async function fetchTeamForm(teamName) {
  const encoded = encodeURIComponent(teamName);
  return apiFetch(`/api/teams/${encoded}/form`, {
    cache: "no-store",
  });
}

export async function predictMatch(homeTeam, awayTeam) {
  return apiFetch("/api/predict", {
    method: "POST",
    body: JSON.stringify({
      home_team: homeTeam,
      away_team: awayTeam,
    }),
    cache: "no-store",
  });
}

export async function compareTeams(teamA, teamB, season) {
  const payload = {
    team_a: teamA,
    team_b: teamB,
  };

  if (season?.trim()) {
    payload.season = season.trim();
  }

  return apiFetch("/api/compare", {
    method: "POST",
    body: JSON.stringify(payload),
    cache: "no-store",
  });
}

export async function chat(message, conversationId) {
  const payload = {
    message,
  };

  if (conversationId) {
    payload.conversation_id = conversationId;
  }

  return apiFetch("/api/chat", {
    method: "POST",
    body: JSON.stringify(payload),
    cache: "no-store",
  });
}
