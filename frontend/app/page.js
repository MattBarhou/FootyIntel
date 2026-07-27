import Link from "next/link";
import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import TeamLogo from "@/components/ui/TeamLogo";

const FEATURES = [
  {
    step: "01",
    title: "Predict",
    description:
      "Run the ML model on any fixture. Get home, draw, and away probabilities built from rolling form and head-to-head data.",
    href: "/predict",
    accent: "red",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="2">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
      </svg>
    ),
  },
  {
    step: "02",
    title: "Compare",
    description:
      "Pit two clubs against each other across the season — points per game, goal difference, shots on target, and more.",
    href: "/compare",
    accent: "blue",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="2">
        <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21 3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
      </svg>
    ),
  },
  {
    step: "03",
    title: "Form",
    description:
      "Browse every team in the sidebar. Tap any club to see their last five results, points, and goals at a glance.",
    href: null,
    accent: "yellow",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="2">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z" />
      </svg>
    ),
  },
];

const TIMELINE = [
  {
    title: "Machine Learning",
    description:
      "A random forest classifier trained on historical Premier League data — rolling form, home/away splits, head-to-head, and rest days.",
  },
  {
    title: "Statistical Engine",
    description:
      "Season metrics aggregated and scored with a weighted blend of points per game, goal difference, shots on target, and win rate.",
  },
  {
    title: "Live Form Data",
    description:
      "Every team's last five results pulled from match data, displayed as an at-a-glance form strip in the sidebar.",
  },
];

export default function HomePage() {
  return (
    <div className="space-y-16">
      <section className="grid items-stretch gap-0 border-4 border-black lg:grid-cols-2">
        <div className="flex flex-col justify-center bg-white p-8 md:p-12">
          <SectionLabel>Premier League Intelligence</SectionLabel>
          <h1 className="mt-4 text-4xl font-black uppercase leading-[0.9] tracking-tighter sm:text-5xl lg:text-6xl">
            Match
            <br />
            Insight.
          </h1>
          <p className="mt-5 max-w-md text-base font-medium leading-relaxed text-[#121212]/75 lg:text-lg">
            Predict outcomes, compare team performance, and explore recent form — powered by
            machine learning and live Premier League data.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/predict" className="bauhaus-btn bauhaus-btn-red">
              Predict Match
            </Link>
            <Link href="/compare" className="bauhaus-btn bauhaus-btn-outline">
              Compare Teams
            </Link>
          </div>
        </div>

        <div className="relative overflow-hidden border-t-4 border-black bg-[#1040C0] p-8 text-white md:p-12 lg:border-l-4 lg:border-t-0">
          <div className="pointer-events-none absolute -right-8 top-8 h-24 w-24 rounded-full border-4 border-white/30 bg-[#D02020]/40" />
          <div className="pointer-events-none absolute bottom-12 left-8 h-16 w-16 rotate-45 border-4 border-white/30 bg-[#F0C020]/50" />
          <div className="pointer-events-none absolute right-16 bottom-8 h-0 w-0 border-x-20 border-b-[35px] border-x-transparent border-b-[#F0C020]/40" />

          <div className="relative">
            <span className="text-xs font-bold uppercase tracking-widest text-white/70">
              Sample Prediction
            </span>
            <div className="mt-6 flex items-center justify-between gap-3">
              <div className="text-center">
                <TeamLogo teamName="Arsenal" size="md" className="mx-auto" />
                <p className="mt-2 text-sm font-bold uppercase">Arsenal</p>
              </div>
              <span className="vs-badge border-white text-white">VS</span>
              <div className="text-center">
                <TeamLogo teamName="Chelsea" size="md" className="mx-auto" />
                <p className="mt-2 text-sm font-bold uppercase">Chelsea</p>
              </div>
            </div>
            <div className="pitch-divider my-6 opacity-40" />
            <div className="space-y-3">
              {[
                { label: "Home Win", value: 48, cls: "prob-bar-home" },
                { label: "Draw", value: 27, cls: "prob-bar-draw" },
                { label: "Away Win", value: 25, cls: "prob-bar-away" },
              ].map((row) => (
                <div key={row.label}>
                  <div className="mb-1 flex justify-between text-xs font-bold uppercase tracking-wider">
                    <span>{row.label}</span>
                    <span className="font-mono">{row.value}%</span>
                  </div>
                  <div className="prob-bar border-white">
                    <div className={`prob-bar-fill ${row.cls}`} style={{ width: `${row.value}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section>
        <SectionLabel>Features</SectionLabel>
        <h2 className="mt-3 text-3xl font-black uppercase tracking-tighter md:text-4xl">
          Everything You Need
        </h2>
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          {FEATURES.map((feature) => (
            <GlassCard
              key={feature.step}
              hover
              accent={feature.accent}
              className="flex flex-col"
              padding="p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex h-12 w-12 items-center justify-center border-2 border-black bg-white shadow-[3px_3px_0px_0px_#121212]">
                  {feature.icon}
                </div>
                <span className="font-mono text-2xl font-black text-[#121212]/25">
                  {feature.step}
                </span>
              </div>
              <h3 className="mt-5 text-lg font-black uppercase tracking-tight">{feature.title}</h3>
              <p className="mt-2 flex-1 text-sm font-medium leading-relaxed text-[#121212]/65">
                {feature.description}
              </p>
              {feature.href ? (
                <Link
                  href={feature.href}
                  className="mt-5 inline-flex items-center gap-1 text-sm font-bold uppercase tracking-wider text-[#1040C0] hover:underline"
                >
                  Explore →
                </Link>
              ) : (
                <p className="mt-5 text-sm font-bold uppercase tracking-wider text-[#121212]/40">
                  Use sidebar →
                </p>
              )}
            </GlassCard>
          ))}
        </div>
      </section>

      <section className="border-y-4 border-black bg-[#F0C020] px-6 py-12 md:px-8 md:py-16">
        <SectionLabel>How It Works</SectionLabel>
        <h2 className="mt-3 text-3xl font-black uppercase tracking-tighter md:text-4xl">
          Under The Hood
        </h2>
        <div className="relative mt-10">
          <div className="timeline-line hidden md:block" />
          <div className="grid gap-8 md:grid-cols-3">
            {TIMELINE.map((item, index) => (
              <div key={item.title} className="relative bg-white/20 p-4 md:bg-transparent md:p-0">
                <div className="mb-4 flex h-10 w-10 items-center justify-center border-2 border-black bg-white text-sm font-black shadow-[3px_3px_0px_0px_#121212]">
                  {index + 1}
                </div>
                <h3 className="font-black uppercase tracking-tight">{item.title}</h3>
                <p className="mt-2 text-sm font-medium leading-relaxed text-[#121212]/75">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
