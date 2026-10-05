import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

export interface OperatorRowProps {
  op: string;
  desc: string;
  onClick?: (op: string) => void;
}

export const OperatorRow: React.FC<OperatorRowProps> = ({ op, desc, onClick }) => {
  return (
    <div
      onClick={() => onClick && onClick(op)}
      style={{
        display: "flex",
        alignItems: "baseline",
        justifyContent: "space-between",
        gap: 12,
        padding: "6px 10px",
        borderRadius: 6,
        background: COLORS.base,
        border: `1px solid ${COLORS.border}`,
        cursor: onClick ? "pointer" : "default",
        transition: "border-color 80ms ease",
      }}
      onMouseEnter={(e) => {
        if (onClick) {
          (e.currentTarget as HTMLDivElement).style.borderColor = COLORS.accent;
        }
      }}
      onMouseLeave={(e) => {
        if (onClick) {
          (e.currentTarget as HTMLDivElement).style.borderColor = COLORS.border;
        }
      }}
    >
      <code
        style={{
          fontFamily: FONTS.mono,
          fontSize: 12,
          color: COLORS.mono,
          flexShrink: 0,
        }}
      >
        {op}
      </code>
      <span
        style={{
          fontFamily: FONTS.sans,
          fontSize: 11,
          color: COLORS.textSecondary,
          textAlign: "right",
        }}
      >
        {desc}
      </span>
    </div>
  );
};
