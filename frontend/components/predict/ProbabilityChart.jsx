import { PREDICTED_RESULT_LABELS } from "@/lib/constants";
import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";

function formatPercent(value) {
  return `${(value * 100).toFixed(1)}%`;
}

export default function ProbabilityChart({ prediction }) {
  const outcomes = [
    {
      key: "home",
      label: prediction.home_team,
      shortLabel: "Home",
      value: prediction.home_win_probability,
      barClass: "prob-bar-home",
      isPredicted: prediction.predicted_result === "H",
    },
    {
      key: "draw",
      label: "Draw",
      shortLabel: "Draw",
      value: prediction.draw_probability,
      barClass: "prob-bar-draw",
      isPredicted: prediction.predicted_result === "D",
    },
    {
      key: "away",
      label: prediction.away_team,
      shortLabel: "Away",
      value: prediction.away_win_probability,
      barClass: "prob-bar-away",
      isPredicted: prediction.predicted_result === "A",
    },
  ];

  const predictedLabel = PREDICTED_RESULT_LABELS[prediction.predicted_result];
  const predictedTeam =
    prediction.predicted_result === "H"
      ? prediction.home_team
      : prediction.predicted_result === "A"
        ? prediction.away_team
        : null;

  return (
    <GlassCard aria-live="polite" accent="red">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <SectionLabel>Result</SectionLabel>
          <h3 className="mt-2 text-2xl font-black uppercase tracking-tight">
            {prediction.home_team}{" "}
            <span className="text-[#121212]/35">vs</span> {prediction.away_team}
          </h3>
        </div>
        <div className="border-2 border-black bg-[#D02020] px-4 py-1.5 text-sm font-bold uppercase tracking-wider text-white shadow-[3px_3px_0px_0px_#121212]">
          {predictedTeam ? `${predictedTeam} — ${predictedLabel}` : predictedLabel}
        </div>
      </div>

      <div className="pitch-divider my-6" />

      <div className="grid gap-4 sm:grid-cols-3" aria-label="Outcome probabilities">
        {outcomes.map((outcome) => (
          <div
            key={outcome.key}
            className={`outcome-card ${outcome.isPredicted ? "outcome-card-predicted" : ""}`}
          >
            {outcome.isPredicted ? (
              <span className="mb-2 inline-block border-2 border-black bg-[#F0C020] px-2 py-0.5 text-[0.65rem] font-black uppercase tracking-widest">
                Most Likely
              </span>
            ) : (
              <span className="mb-2 inline-block text-[0.65rem] font-bold uppercase tracking-widest text-[#121212]/40">
                {outcome.shortLabel}
              </span>
            )}
            <p className="truncate text-sm font-bold uppercase">{outcome.label}</p>
            <p className="mt-1 font-mono text-3xl font-black tabular-nums">
              {formatPercent(outcome.value)}
            </p>
            <div className="prob-bar mt-3">
              <div
                className={`prob-bar-fill ${outcome.barClass}`}
                style={{ width: `${outcome.value * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
