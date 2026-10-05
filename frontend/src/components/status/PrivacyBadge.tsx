import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

export const PrivacyBadge: React.FC = () => {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "12px 14px",
        background: `${COLORS.success}0D`,
        border: `1px solid ${COLORS.success}30`,
        borderRadius: 8,
      }}
    >
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden>
        <path
          d="M9 2L3 4.5V9c0 3.3 2.5 6.4 6 7 3.5-.6 6-3.7 6-7V4.5L9 2z"
          fill={`${COLORS.success}20`}
          stroke={COLORS.success}
          strokeWidth="1.25"
          strokeLinejoin="round"
        />
        <path
          d="M6.5 9l1.8 1.8L12 7"
          stroke={COLORS.success}
          strokeWidth="1.25"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
        <span
          style={{
            fontFamily: FONTS.sans,
            fontSize: 13,
            fontWeight: 600,
            color: COLORS.success,
          }}
        >
          100% Local
        </span>
        <span
          style={{
            fontFamily: FONTS.sans,
            fontSize: 11,
            color: COLORS.textSecondary,
          }}
        >
          No data ever leaves this device
        </span>
      </div>
    </div>
  );
};
