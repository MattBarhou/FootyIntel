import { getTeams } from "@/lib/api";
import PredictPanel from "@/components/predict/PredictPanel";
import PageShell from "@/components/ui/PageShell";

export const metadata = {
  title: "Predict Match — FootyIntel",
  description: "Predict Premier League match outcomes using machine learning.",
};

export default async function PredictPage() {
  const { teams } = await getTeams();

  return (
    <PageShell
      kicker="Machine Learning"
      title="Match Prediction"
      description="Select two teams to predict the outcome. The model returns home win, draw, and away win probabilities."
    >
      <PredictPanel teams={teams} />
    </PageShell>
  );
}
