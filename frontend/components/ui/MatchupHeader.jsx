import { getTeamInitials } from "@/lib/constants";

export default function MatchupHeader({ homeTeam, awayTeam }) {
  return (
    <div className="flex items-center justify-center gap-4 py-2">
      <div className="flex flex-1 flex-col items-end gap-1.5 text-right">
        {homeTeam ? (
          <>
            <span className="team-avatar team-avatar-a">{getTeamInitials(homeTeam)}</span>
            <span className="max-w-[8rem] truncate text-sm font-bold uppercase sm:max-w-none">
              {homeTeam}
            </span>
            <span className="text-xs font-bold uppercase tracking-widest text-[#121212]/50">
              Home
            </span>
          </>
        ) : (
          <span className="text-sm font-medium text-[#121212]/40">Select home</span>
        )}
      </div>

      <div className="vs-badge shrink-0">VS</div>

      <div className="flex flex-1 flex-col items-start gap-1.5 text-left">
        {awayTeam ? (
          <>
            <span className="team-avatar team-avatar-b">{getTeamInitials(awayTeam)}</span>
            <span className="max-w-[8rem] truncate text-sm font-bold uppercase sm:max-w-none">
              {awayTeam}
            </span>
            <span className="text-xs font-bold uppercase tracking-widest text-[#121212]/50">
              Away
            </span>
          </>
        ) : (
          <span className="text-sm font-medium text-[#121212]/40">Select away</span>
        )}
      </div>
    </div>
  );
}
