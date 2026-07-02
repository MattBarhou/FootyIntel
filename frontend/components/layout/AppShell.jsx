"use client";

import { useState } from "react";
import Navbar from "@/components/layout/Navbar";
import TeamsSidebar from "@/components/layout/TeamsSidebar";

export default function AppShell({ teams, children }) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="drawer lg:drawer-open">
      <input
        id="teams-drawer"
        type="checkbox"
        className="drawer-toggle"
        checked={drawerOpen}
        onChange={(event) => setDrawerOpen(event.target.checked)}
      />

      <div className="drawer-content flex min-h-screen flex-col">
        <Navbar onOpenTeams={() => setDrawerOpen(true)} />
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-10 md:px-8 md:py-12">
          {children}
        </main>
      </div>

      <div className="drawer-side z-50">
        <label
          htmlFor="teams-drawer"
          aria-label="Close teams sidebar"
          className="drawer-overlay bg-[#121212]/40"
          onClick={() => setDrawerOpen(false)}
        />
        <div className="h-full w-80 max-w-[88vw] border-r-4 border-black shadow-[8px_0px_0px_0px_#121212]">
          <TeamsSidebar teams={teams} className="h-full w-full" />
        </div>
      </div>
    </div>
  );
}
