import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

interface FooterKbdProps {
  keys: string[];
  label: string;
}

export const FooterKbd: React.FC<FooterKbdProps> = ({ keys, label }) => {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        color: COLORS.textSecondary,
        fontSize: 11,
      }}
    >
      {keys.map((k) => (
        <kbd
          key={k}
          style={{
            fontFamily: FONTS.mono,
            fontSize: 10,
            background: COLORS.border,
            color: COLORS.textPrimary,
            padding: "1px 5px",
            borderRadius: 3,
            border: `1px solid ${COLORS.border}`,
            lineHeight: "14px",
          }}
        >
          {k}
        </kbd>
      ))}
      <span style={{ color: COLORS.textSecondary }}>{label}</span>
    </span>
  );
};
