"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import PillNavLink from "@/components/ui/PillNavLink";

const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/predict", label: "Predict" },
  { href: "/compare", label: "Compare" },
];

function isActive(pathname, href) {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname.startsWith(href);
}

export default function Navbar({ onOpenTeams }) {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b-4 border-black bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 md:px-6">
        <div className="flex-none lg:hidden">
          <button
            type="button"
            className="flex h-10 w-10 items-center justify-center border-2 border-black bg-white shadow-[3px_3px_0px_0px_#121212] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none"
            onClick={onOpenTeams}
            aria-label="Open teams sidebar"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              className="h-5 w-5 stroke-current"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>

        <Link href="/" className="group flex items-center gap-3">
          <Image
            src="/epl.jpg"
            alt="Premier League"
            width={36}
            height={36}
            className="h-9 w-9 rounded-lg object-cover"
          />
          <span className="text-lg font-black uppercase tracking-tight">
            Footy<span className="text-[#1040C0]">Intel</span>
          </span>
        </Link>

        <nav className="ml-auto hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => (
            <PillNavLink
              key={link.href}
              href={link.href}
              active={isActive(pathname, link.href)}
            >
              {link.label}
            </PillNavLink>
          ))}
        </nav>

        <div className="ml-auto flex md:hidden">
          <div className="dropdown dropdown-end">
            <div
              tabIndex={0}
              role="button"
              className="flex h-10 w-10 items-center justify-center border-2 border-black bg-white shadow-[3px_3px_0px_0px_#121212]"
              aria-label="Open navigation menu"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                className="h-5 w-5 stroke-current"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4 6h16M4 12h16M4 18h7"
                />
              </svg>
            </div>
            <ul
              tabIndex={0}
              className="menu dropdown-content z-50 mt-3 w-48 border-2 border-black bg-white p-2 shadow-[4px_4px_0px_0px_#121212]"
            >
              {NAV_LINKS.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className={`font-bold uppercase tracking-wider ${
                      isActive(pathname, link.href)
                        ? "bg-[#1040C0] text-white"
                        : "text-[#121212]"
                    }`}
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </header>
  );
}
