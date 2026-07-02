"use client";

import { useMemo, useState, useTransition } from "react";
import { fetchTeamFormAction } from "@/lib/actions";
import ErrorAlert from "@/components/ui/ErrorAlert";
import LoadingState from "@/components/ui/LoadingState";
import TeamFormPanel from "@/components/teams/TeamFormPanel";
import TeamSearch from "@/components/teams/TeamSearch";

export default function TeamsSidebar({ teams, className = "" }) {
  const [query, setQuery] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("");
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  const filteredTeams = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return teams;
    }
    return teams.filter((team) => team.name.toLowerCase().includes(normalized));
  }, [query, teams]);

  function handleSelectTeam(teamName) {
    setSelectedTeam(teamName);
    setForm(null);
    setError("");

    startTransition(async () => {
      const result = await fetchTeamFormAction(teamName);
      if (result.error) {
        setError(result.error);
        return;
      }
      setForm(result.data);
    });
  }

  return (
    <aside className={`flex h-full flex-col bg-white ${className}`}>
      <div className="border-b-4 border-black bg-[#F0C020] px-4 py-5">
        <h2 className="text-xl font-black uppercase tracking-tight">Teams</h2>
        <p className="mt-1 text-xs font-bold uppercase tracking-widest text-[#121212]/60">
          {teams.length} Premier League clubs
        </p>
        <div className="mt-4">
          <TeamSearch value={query} onChange={setQuery} />
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-3">
        <ul className="flex flex-col gap-1">
          {filteredTeams.map((team) => (
            <li key={team.name}>
              <button
                type="button"
                className={`team-row ${
                  selectedTeam === team.name ? "team-row-selected" : ""
                }`}
                onClick={() => handleSelectTeam(team.name)}
              >
                {team.name}
              </button>
            </li>
          ))}
        </ul>
        {filteredTeams.length === 0 ? (
          <p className="px-3 py-6 text-center text-sm font-medium text-[#121212]/45">
            No teams match your search.
          </p>
        ) : null}
      </div>

      <div className="border-t-4 border-black bg-[#F0F0F0] p-4" aria-live="polite">
        {isPending ? <LoadingState label="Loading form..." /> : null}
        {!isPending && error ? <ErrorAlert message={error} /> : null}
        {!isPending && !error ? <TeamFormPanel form={form} /> : null}
        {!isPending && !error && !form && selectedTeam === "" ? (
          <p className="text-center text-sm font-medium text-[#121212]/45">
            Select a team to view recent form.
          </p>
        ) : null}
      </div>
    </aside>
  );
}
