"use client";

export default function TeamSelect({
  id,
  label,
  teams,
  value,
  onChange,
  disabled = false,
  excludeTeam = "",
}) {
  const options = teams.filter((team) => team.name !== excludeTeam);

  return (
    <label className="flex w-full flex-col gap-2" htmlFor={id}>
      <span className="text-xs font-bold uppercase tracking-widest text-[#121212]/70">
        {label}
      </span>
      <select
        id={id}
        className="select-bauhaus w-full px-4 py-3 text-sm font-semibold disabled:opacity-50"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
      >
        <option value="">Select a team</option>
        {options.map((team) => (
          <option key={team.name} value={team.name}>
            {team.name}
          </option>
        ))}
      </select>
    </label>
  );
}
