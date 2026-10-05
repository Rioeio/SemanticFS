import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

interface ScoreChipProps {
  score: number;
}

export const ScoreChip: React.FC<ScoreChipProps> = ({ score }) => {
  const pct = Math.round(score * 100);
  const opacity = 0.5 + score * 0.5;

  return (
    <span
      style={{
        fontFamily: FONTS.mono,
        fontSize: 11,
        fontWeight: 500,
        color: COLORS.accent,
        opacity,
        letterSpacing: "0.02em",
        whiteSpace: "nowrap",
      }}
    >
      {pct}%
    </span>
  );
};
