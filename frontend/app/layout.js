import { Outfit } from "next/font/google";
import { getTeams } from "@/lib/api";
import AppShell from "@/components/layout/AppShell";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  weight: ["400", "500", "700", "900"],
});

export const metadata = {
  title: "FootyIntel — EPL Match Intelligence",
  description:
    "Premier League match predictions, team comparisons, and form analysis powered by machine learning.",
};

export default async function RootLayout({ children }) {
  const { teams } = await getTeams();

  return (
    <html lang="en" data-theme="footyintel" className={`${outfit.variable} h-full`}>
      <body className="bauhaus-canvas min-h-full font-medium text-[#121212] antialiased">
        <AppShell teams={teams}>{children}</AppShell>
      </body>
    </html>
  );
}
