import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

interface EmptyStateProps {
  query: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ query }) => {
  return (
    <div
      style={{
        padding: "32px 24px",
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 8,
      }}
    >
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" aria-hidden>
        <circle cx="14" cy="14" r="9" stroke={COLORS.border} strokeWidth="1.5" />
        <path
          d="M21 21L28 28"
          stroke={COLORS.border}
          strokeWidth="1.5"
          strokeLinecap="round"
        />
        <path
          d="M10 14h8M14 10v8"
          stroke={COLORS.textSecondary}
          strokeWidth="1.25"
          strokeLinecap="round"
          opacity="0.4"
        />
      </svg>
      <p
        style={{
          fontFamily: FONTS.sans,
          fontSize: 13,
          color: COLORS.textSecondary,
          margin: 0,
        }}
      >
        No files match{" "}
        <span style={{ color: COLORS.highlight, fontStyle: "italic" }}>
          "{query}"
        </span>
      </p>
      <p
        style={{
          fontFamily: FONTS.mono,
          fontSize: 11,
          color: COLORS.textSecondary,
          opacity: 0.6,
          margin: 0,
        }}
      >
        Try broader terms or check index coverage
      </p>
    </div>
  );
};
