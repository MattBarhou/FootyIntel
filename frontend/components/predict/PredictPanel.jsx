"use client";

import { useState, useTransition } from "react";
import { predictMatchAction } from "@/lib/actions";
import ProbabilityChart from "@/components/predict/ProbabilityChart";
import TeamSelect from "@/components/teams/TeamSelect";
import ErrorAlert from "@/components/ui/ErrorAlert";
import GlassCard from "@/components/ui/GlassCard";
import LoadingState from "@/components/ui/LoadingState";
import MatchupHeader from "@/components/ui/MatchupHeader";

export default function PredictPanel({ teams }) {
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setPrediction(null);

    startTransition(async () => {
      const result = await predictMatchAction({
        home_team: homeTeam,
        away_team: awayTeam,
      });

      if (result.error) {
        setError(result.error);
        return;
      }

      setPrediction(result.data);
    });
  }

  return (
    <div className="space-y-6">
      <GlassCard accent="red">
        <form onSubmit={handleSubmit} className="space-y-6">
          <MatchupHeader homeTeam={homeTeam} awayTeam={awayTeam} />

          <div className="pitch-divider" />

          <div className="grid gap-5 md:grid-cols-2">
            <TeamSelect
              id="home-team"
              label="Home Team"
              teams={teams}
              value={homeTeam}
              onChange={setHomeTeam}
              disabled={isPending}
              excludeTeam={awayTeam}
            />
            <TeamSelect
              id="away-team"
              label="Away Team"
              teams={teams}
              value={awayTeam}
              onChange={setAwayTeam}
              disabled={isPending}
              excludeTeam={homeTeam}
            />
          </div>

          <button
            type="submit"
            className="bauhaus-btn bauhaus-btn-red w-full md:w-auto"
            disabled={isPending || !homeTeam || !awayTeam}
          >
            {isPending ? (
              <span className="flex items-center gap-2">
                <span className="loading loading-spinner loading-sm" />
                Predicting...
              </span>
            ) : (
              "Predict Match"
            )}
          </button>
        </form>
      </GlassCard>

      {isPending ? <LoadingState label="Running prediction model..." /> : null}
      {error ? <ErrorAlert message={error} /> : null}
      {prediction ? <ProbabilityChart prediction={prediction} /> : null}
    </div>
  );
}
