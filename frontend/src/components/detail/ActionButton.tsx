import React, { useState } from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

export interface ActionButtonProps {
  label: string;
  onClick: () => void;
  primary?: boolean;
}

export const ActionButton: React.FC<ActionButtonProps> = ({ label, onClick, primary }) => {
  const [hov, setHov] = useState(false);

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        height: 32,
        padding: "0 14px",
        borderRadius: 6,
        border: primary ? "none" : `1px solid ${COLORS.border}`,
        background: primary
          ? COLORS.accent
          : hov
          ? COLORS.border
          : "transparent",
        opacity: primary && hov ? 0.9 : 1,
        color: primary ? COLORS.base : COLORS.textSecondary,
        fontFamily: FONTS.sans,
        fontSize: 13,
        fontWeight: primary ? 600 : 400,
        cursor: "pointer",
        transition: "background 80ms ease, opacity 80ms ease, color 80ms ease",
      }}
    >
      {label}
    </button>
  );
};
