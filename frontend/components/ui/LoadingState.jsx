import GlassCard from "@/components/ui/GlassCard";

export default function LoadingState({ label = "Loading..." }) {
  return (
    <GlassCard className="flex items-center justify-center gap-3 py-10" padding="p-6" accent="yellow">
      <span className="loading loading-spinner loading-md text-[#121212]" />
      <span className="text-sm font-bold uppercase tracking-wider text-[#121212]/70">{label}</span>
    </GlassCard>
  );
}
