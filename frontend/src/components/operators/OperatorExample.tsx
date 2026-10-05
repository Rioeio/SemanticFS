import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

export interface OperatorExampleProps {
  label?: string;
  query?: string;
  onSelectExample?: (query: string) => void;
}

export const OperatorExample: React.FC<OperatorExampleProps> = ({
  label = "example:",
  query = "tax receipts ext:pdf +2025 in:~/Documents",
  onSelectExample,
}) => {
  return (
    <div
      onClick={() => onSelectExample && onSelectExample(query)}
      style={{
        marginTop: 4,
        padding: "8px 10px",
        borderRadius: 6,
        background: `${COLORS.accent}0A`,
        border: `1px solid ${COLORS.accent}20`,
        cursor: onSelectExample ? "pointer" : "default",
        transition: "border-color 80ms ease",
      }}
      onMouseEnter={(e) => {
        if (onSelectExample) {
          (e.currentTarget as HTMLDivElement).style.borderColor = COLORS.accent;
        }
      }}
      onMouseLeave={(e) => {
        if (onSelectExample) {
          (e.currentTarget as HTMLDivElement).style.borderColor = `${COLORS.accent}20`;
        }
      }}
    >
      <p
        style={{
          fontFamily: FONTS.mono,
          fontSize: 11,
          color: COLORS.textSecondary,
          margin: 0,
          lineHeight: 1.6,
        }}
      >
        <span style={{ color: COLORS.accent }}>{label}</span>{" "}
        <span style={{ color: COLORS.textPrimary }}>{query}</span>
      </p>
    </div>
  );
};
