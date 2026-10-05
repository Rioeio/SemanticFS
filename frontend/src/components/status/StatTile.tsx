import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

export interface StatTileProps {
  label: string;
  value: string;
}

export const StatTile: React.FC<StatTileProps> = ({ label, value }) => {
  return (
    <div
      style={{
        padding: "10px 12px",
        borderRadius: 8,
        background: COLORS.base,
        border: `1px solid ${COLORS.border}`,
        display: "flex",
        flexDirection: "column",
        gap: 4,
      }}
    >
      <span
        style={{
          fontFamily: FONTS.mono,
          fontSize: 18,
          fontWeight: 600,
          color: COLORS.textPrimary,
          letterSpacing: "-0.02em",
        }}
      >
        {value}
      </span>
      <span
        style={{
          fontFamily: FONTS.sans,
          fontSize: 11,
          color: COLORS.textSecondary,
        }}
      >
        {label}
      </span>
    </div>
  );
};
