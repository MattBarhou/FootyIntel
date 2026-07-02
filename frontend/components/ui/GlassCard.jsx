const ACCENT_DECO = {
  red: "bauhaus-card-deco-red",
  blue: "bauhaus-card-deco-blue",
  yellow: "bauhaus-card-deco-yellow",
};

export default function GlassCard({
  children,
  className = "",
  hover = false,
  padding = "p-6",
  accent = null,
}) {
  return (
    <div
      className={`bauhaus-card ${padding} ${hover ? "bauhaus-card-hover" : ""} ${className}`.trim()}
    >
      {accent && ACCENT_DECO[accent] ? (
        <span className={`bauhaus-card-deco ${ACCENT_DECO[accent]}`} aria-hidden="true" />
      ) : null}
      {children}
    </div>
  );
}
