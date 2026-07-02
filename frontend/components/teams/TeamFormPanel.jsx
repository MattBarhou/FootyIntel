import FormResultPills from "@/components/ui/FormResultPills";
import StatChip from "@/components/ui/StatChip";
import { getTeamInitials } from "@/lib/constants";

export default function TeamFormPanel({ form }) {
  if (!form) {
    return null;
  }

  return (
    <div className="bauhaus-card relative p-4">
      <span className="bauhaus-card-deco bauhaus-card-deco-yellow" aria-hidden="true" />
      <div className="flex items-center gap-3">
        <span className="team-avatar team-avatar-a text-sm">{getTeamInitials(form.team)}</span>
        <div>
          <h3 className="font-black uppercase tracking-tight text-[#121212]">{form.team}</h3>
          <p className="text-xs font-bold uppercase tracking-widest text-[#121212]/50">
            Last 5 matches
          </p>
        </div>
      </div>

      <div className="mt-4">
        <FormResultPills results={form.last_5_results} team={form.team} />
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2">
        <StatChip label="Points" value={form.points_last_5} highlight />
        <StatChip label="GF" value={form.goals_for_last_5} />
        <StatChip label="GA" value={form.goals_against_last_5} />
      </div>
    </div>
  );
}
