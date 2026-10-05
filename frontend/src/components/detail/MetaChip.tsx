import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

export interface MetaChipProps {
  label: string;
}

export const MetaChip: React.FC<MetaChipProps> = ({ label }) => {
  return (
    <span
      style={{
        fontFamily: FONTS.mono,
        fontSize: 11,
        color: COLORS.textSecondary,
        padding: "2px 6px",
        borderRadius: 4,
        border: `1px solid ${COLORS.border}`,
      }}
    >
      {label}
    </span>
  );
};
