import Link from "next/link";

export default function PillNavLink({ href, active, children, onClick }) {
  const className = `bauhaus-nav-pill ${active ? "bauhaus-nav-pill-active" : ""}`;

  if (onClick) {
    return (
      <button type="button" className={className} onClick={onClick}>
        {children}
      </button>
    );
  }

  return (
    <Link href={href} className={className}>
      {children}
    </Link>
  );
}
