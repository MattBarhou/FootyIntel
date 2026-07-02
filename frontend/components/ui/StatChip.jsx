export default function StatChip({ label, value, highlight = false }) {
  return (
    <div className={`stat-chip px-3 py-2.5 ${highlight ? "stat-chip-highlight" : ""}`}>
      <div className="text-[0.65rem] font-bold uppercase tracking-widest text-[#121212]/55">
        {label}
      </div>
      <div className="mt-0.5 text-xl font-black tabular-nums text-[#121212]">{value}</div>
    </div>
  );
}
