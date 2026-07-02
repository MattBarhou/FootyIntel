import SectionLabel from "@/components/ui/SectionLabel";

export default function PageHeader({ kicker, title, description }) {
  return (
    <header className="mb-8 border-b-4 border-black pb-6">
      {kicker ? <SectionLabel>{kicker}</SectionLabel> : null}
      <h1
        className={`text-3xl font-black uppercase leading-[0.95] tracking-tighter md:text-4xl ${
          kicker ? "mt-3" : ""
        }`}
      >
        {title}
      </h1>
      {description ? (
        <p className="mt-3 max-w-2xl text-base leading-relaxed font-medium text-[#121212]/75">
          {description}
        </p>
      ) : null}
    </header>
  );
}
