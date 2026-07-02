export default function GeometricLogo({ size = "md" }) {
  const shapeSize = size === "sm" ? "h-2 w-2" : "h-2.5 w-2.5";

  return (
    <span className="flex items-end gap-0.5" aria-hidden="true">
      <span className={`${shapeSize} rounded-full bg-[#D02020] border border-black`} />
      <span className={`${shapeSize} bg-[#1040C0] border border-black`} />
      <span
        className={`${shapeSize} bg-[#F0C020] border border-black`}
        style={{ clipPath: "polygon(50% 0%, 0% 100%, 100% 100%)" }}
      />
    </span>
  );
}
