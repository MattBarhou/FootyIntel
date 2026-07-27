"use client";

import { useEffect, useRef, useState } from "react";
import TeamLogo from "@/components/ui/TeamLogo";

export default function TeamPicker({
  id,
  label,
  teams,
  value,
  onChange,
  disabled = false,
  excludeTeam = "",
}) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);
  const options = teams.filter((team) => team.name !== excludeTeam);

  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleSelect(teamName) {
    onChange(teamName);
    setOpen(false);
  }

  return (
    <div ref={containerRef} className="relative flex w-full flex-col gap-2">
      <span
        id={`${id}-label`}
        className="text-xs font-bold uppercase tracking-widest text-[#121212]/70"
      >
        {label}
      </span>
      <button
        id={id}
        type="button"
        aria-labelledby={`${id}-label`}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="select-bauhaus flex w-full items-center gap-3 px-4 py-3 text-left text-sm font-semibold disabled:opacity-50"
        onClick={() => !disabled && setOpen((current) => !current)}
        disabled={disabled}
      >
        {value ? (
          <>
            <TeamLogo teamName={value} size="sm" />
            <span className="truncate">{value}</span>
          </>
        ) : (
          <span className="text-[#121212]/45">Select a team</span>
        )}
      </button>

      {open ? (
        <ul
          role="listbox"
          aria-labelledby={`${id}-label`}
          className="absolute top-full z-50 mt-1 max-h-60 w-full overflow-y-auto border-2 border-black bg-white p-1 shadow-[4px_4px_0px_0px_#121212]"
        >
          {options.map((team) => (
            <li key={team.name} role="option" aria-selected={value === team.name}>
              <button
                type="button"
                className={`flex w-full items-center gap-3 px-3 py-2 text-left text-sm font-semibold hover:bg-[#F0F0F0] ${
                  value === team.name ? "bg-[#1040C0] text-white hover:bg-[#1040C0]" : ""
                }`}
                onClick={() => handleSelect(team.name)}
              >
                <TeamLogo teamName={team.name} size="sm" />
                <span className="truncate">{team.name}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
