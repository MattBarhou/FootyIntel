import { BETTER_TEAM_LABELS, COMPARE_STAT_LABELS, getTeamInitials } from "@/lib/constants";
import GlassCard from "@/components/ui/GlassCard";

function formatStatValue(key, value) {
  if (key === "win_rate") {
    return `${(value * 100).toFixed(1)}%`;
  }
  if (Number.isInteger(value)) {
    return value.toString();
  }
  return value.toFixed(2);
}

function DesktopStatRow({ label, valueA, valueB, leader, striped }) {
  return (
    <tr className={striped ? "bg-[#F0F0F0]" : "bg-white"}>
      <td
        className={`hidden py-3.5 pr-4 text-right font-mono text-sm md:table-cell ${
          leader === "a" ? "font-black text-[#1040C0]" : "text-[#121212]/55"
        }`}
      >
        {valueA}
      </td>
      <td className="hidden py-3.5 text-center text-xs font-bold uppercase tracking-wider text-[#121212]/50 md:table-cell">
        {label}
      </td>
      <td
        className={`hidden py-3.5 pl-4 font-mono text-sm md:table-cell ${
          leader === "b" ? "font-black text-[#1040C0]" : "text-[#121212]/55"
        }`}
      >
        {valueB}
      </td>
      <td className="p-3 md:hidden" colSpan={3}>
        <div className="border-2 border-black bg-white px-3 py-2.5 shadow-[3px_3px_0px_0px_#121212]">
          <p className="text-xs font-bold uppercase tracking-wider text-[#121212]/50">{label}</p>
          <div className="mt-1 flex justify-between font-mono text-sm">
            <span className={leader === "a" ? "font-black text-[#1040C0]" : "text-[#121212]/55"}>
              {valueA}
            </span>
            <span className="text-[#121212]/30">·</span>
            <span className={leader === "b" ? "font-black text-[#1040C0]" : "text-[#121212]/55"}>
              {valueB}
            </span>
          </div>
        </div>
      </td>
    </tr>
  );
}

export default function StatsComparison({ comparison }) {
  const statKeys = Object.keys(COMPARE_STAT_LABELS);
  const betterLabel = BETTER_TEAM_LABELS[comparison.better_team] || comparison.better_team;
  const leaderName =
    comparison.better_team === "team_a"
      ? comparison.team_a
      : comparison.better_team === "team_b"
        ? comparison.team_b
        : null;

  return (
    <div className="space-y-6" aria-live="polite">
      <div className="border-4 border-black bg-[#F0C020] p-6 shadow-[6px_6px_0px_0px_#121212]">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="team-avatar team-avatar-a">{getTeamInitials(comparison.team_a)}</span>
            <span className="vs-badge text-[0.6rem]">VS</span>
            <span className="team-avatar team-avatar-b">{getTeamInitials(comparison.team_b)}</span>
          </div>
          <span className="border-2 border-black bg-white px-3 py-1 text-xs font-bold uppercase tracking-widest shadow-[3px_3px_0px_0px_#121212]">
            Season {comparison.season}
          </span>
        </div>

        <div className="mt-5">
          <h3 className="text-2xl font-black uppercase tracking-tight">
            {leaderName ? `${leaderName} Leads` : betterLabel}
          </h3>
        </div>
        <p className="summary-quote mt-4 text-sm font-medium leading-relaxed">
          {comparison.summary}
        </p>
      </div>

      <GlassCard padding="p-0" accent="blue">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b-4 border-black bg-[#1040C0] text-white">
                <th className="hidden py-3 pr-4 text-right text-sm font-black uppercase md:table-cell">
                  <div className="flex items-center justify-end gap-2">
                    <span className="team-avatar team-avatar-a border-white bg-white text-[0.6rem] text-[#1040C0]">
                      {getTeamInitials(comparison.team_a)}
                    </span>
                    {comparison.team_a}
                  </div>
                </th>
                <th className="hidden py-3 text-center text-xs font-black uppercase tracking-widest md:table-cell">
                  Stat
                </th>
                <th className="hidden py-3 pl-4 text-left text-sm font-black uppercase md:table-cell">
                  <div className="flex items-center gap-2">
                    <span className="team-avatar team-avatar-b border-white text-[0.6rem]">
                      {getTeamInitials(comparison.team_b)}
                    </span>
                    {comparison.team_b}
                  </div>
                </th>
                <th className="py-3 text-center text-xs font-black uppercase tracking-widest md:hidden">
                  Comparison
                </th>
              </tr>
            </thead>
            <tbody>
              {statKeys.map((key, index) => {
                const valueA = comparison.team_a_stats[key];
                const valueB = comparison.team_b_stats[key];
                let leader = null;
                if (valueA > valueB) {
                  leader = "a";
                } else if (valueB > valueA) {
                  leader = "b";
                }

                return (
                  <DesktopStatRow
                    key={key}
                    label={COMPARE_STAT_LABELS[key]}
                    valueA={formatStatValue(key, valueA)}
                    valueB={formatStatValue(key, valueB)}
                    leader={leader}
                    striped={index % 2 === 1}
                  />
                );
              })}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
