import SectionLabel from "@/components/ui/SectionLabel";

export default function PageShell({ kicker, title, description, children, className = "" }) {
  return (
    <div className={className}>
      {(kicker || title || description) && (
        <header className="mb-10 border-b-4 border-black pb-8">
          {kicker ? <SectionLabel>{kicker}</SectionLabel> : null}
          {title ? (
            <h1 className="mt-3 text-4xl font-black uppercase leading-[0.95] tracking-tighter sm:text-5xl lg:text-6xl">
              {title}
            </h1>
          ) : null}
          {description ? (
            <p className="mt-4 max-w-2xl text-base leading-relaxed font-medium text-[#121212]/75 lg:text-lg">
              {description}
            </p>
          ) : null}
        </header>
      )}
      {children}
    </div>
  );
}
