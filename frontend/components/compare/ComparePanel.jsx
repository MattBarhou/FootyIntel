"use client";

import { useState, useTransition } from "react";
import { compareTeamsAction } from "@/lib/actions";
import StatsComparison from "@/components/compare/StatsComparison";
import TeamPicker from "@/components/teams/TeamPicker";
import ErrorAlert from "@/components/ui/ErrorAlert";
import GlassCard from "@/components/ui/GlassCard";
import LoadingState from "@/components/ui/LoadingState";
import TeamLogo from "@/components/ui/TeamLogo";

export default function ComparePanel({ teams }) {
  const [teamA, setTeamA] = useState("");
  const [teamB, setTeamB] = useState("");
  const [season, setSeason] = useState("");
  const [comparison, setComparison] = useState(null);
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setComparison(null);

    startTransition(async () => {
      const result = await compareTeamsAction({
        team_a: teamA,
        team_b: teamB,
        season: season || undefined,
      });

      if (result.error) {
        setError(result.error);
        return;
      }

      setComparison(result.data);
    });
  }

  return (
    <div className="space-y-6">
      <GlassCard accent="blue">
        <form onSubmit={handleSubmit} className="space-y-6">
          {(teamA || teamB) && (
            <div className="flex items-center justify-center gap-4 py-2">
              <div className="flex flex-col items-center gap-1">
                <TeamLogo teamName={teamA || null} size="md" variant="a" />
                <span className="text-xs font-bold uppercase tracking-wider text-[#121212]/50">
                  {teamA || "Team A"}
                </span>
              </div>
              <span className="vs-badge">VS</span>
              <div className="flex flex-col items-center gap-1">
                <TeamLogo teamName={teamB || null} size="md" variant="b" />
                <span className="text-xs font-bold uppercase tracking-wider text-[#121212]/50">
                  {teamB || "Team B"}
                </span>
              </div>
            </div>
          )}

          <div className="grid gap-5 md:grid-cols-2">
            <TeamPicker
              id="team-a"
              label="Team A"
              teams={teams}
              value={teamA}
              onChange={setTeamA}
              disabled={isPending}
              excludeTeam={teamB}
            />
            <TeamPicker
              id="team-b"
              label="Team B"
              teams={teams}
              value={teamB}
              onChange={setTeamB}
              disabled={isPending}
              excludeTeam={teamA}
            />
          </div>

          <label className="flex max-w-xs flex-col gap-2">
            <span className="text-xs font-bold uppercase tracking-widest text-[#121212]/70">
              Season (optional)
            </span>
            <input
              type="text"
              className="select-bauhaus px-4 py-3 text-sm font-semibold"
              placeholder="e.g. 23-24"
              value={season}
              onChange={(event) => setSeason(event.target.value)}
              disabled={isPending}
            />
            <span className="text-xs font-medium text-[#121212]/45">
              Leave blank to use the latest season
            </span>
          </label>

          <button
            type="submit"
            className="bauhaus-btn bauhaus-btn-blue w-full md:w-auto"
            disabled={isPending || !teamA || !teamB}
          >
            {isPending ? (
              <span className="flex items-center gap-2">
                <span className="loading loading-spinner loading-sm" />
                Comparing...
              </span>
            ) : (
              "Compare Teams"
            )}
          </button>
        </form>
      </GlassCard>

      {isPending ? <LoadingState label="Comparing team stats..." /> : null}
      {error ? <ErrorAlert message={error} /> : null}
      {comparison ? <StatsComparison comparison={comparison} /> : null}
    </div>
  );
}
