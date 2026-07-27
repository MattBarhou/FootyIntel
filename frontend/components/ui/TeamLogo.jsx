"use client";

import Image from "next/image";
import { useState } from "react";
import { getTeamInitials } from "@/lib/constants";
import { getTeamLogoSrc } from "@/lib/teamLogos";

const SIZE_PX = {
  xs: 20,
  sm: 28,
  md: 44,
  lg: 56,
};

const SIZE_CLASSES = {
  xs: "h-5 w-5",
  sm: "h-7 w-7",
  md: "h-11 w-11",
  lg: "h-14 w-14",
};

export default function TeamLogo({
  teamName,
  size = "md",
  variant,
  className = "",
}) {
  const [failed, setFailed] = useState(false);
  const src = getTeamLogoSrc(teamName);
  const showImage = Boolean(teamName && src && !failed);
  const variantClass =
    variant === "a" ? "team-avatar-a" : variant === "b" ? "team-avatar-b" : "";

  if (!showImage) {
    if (!teamName) {
      return (
        <span
          className={`team-avatar ${variantClass} ${SIZE_CLASSES[size]} ${className}`.trim()}
          aria-hidden="true"
        >
          ?
        </span>
      );
    }

    return (
      <span
        className={`team-avatar ${variantClass} ${SIZE_CLASSES[size]} ${className}`.trim()}
        aria-hidden="true"
      >
        {getTeamInitials(teamName)}
      </span>
    );
  }

  return (
    <Image
      src={src}
      alt={`${teamName} logo`}
      width={SIZE_PX[size]}
      height={SIZE_PX[size]}
      className={`rounded-lg border-2 border-black bg-white object-contain p-0.5 ${SIZE_CLASSES[size]} ${className}`.trim()}
      onError={() => setFailed(true)}
    />
  );
}
