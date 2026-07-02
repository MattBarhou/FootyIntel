import { getTeams } from "@/lib/api";
import ComparePanel from "@/components/compare/ComparePanel";
import PageShell from "@/components/ui/PageShell";

export const metadata = {
  title: "Compare Teams — FootyIntel",
  description: "Compare Premier League team statistics across a season.",
};

export default async function ComparePage() {
  const { teams } = await getTeams();

  return (
    <PageShell
      kicker="Head to Head"
      title="Team Comparison"
      description="Compare two teams across key season metrics and see which side has the edge."
    >
      <ComparePanel teams={teams} />
    </PageShell>
  );
}
