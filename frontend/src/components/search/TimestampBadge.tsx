import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import { recencyOf, relativeTime } from "../../utils/format";
import type { Recency } from "../../types/search";

const RECENCY_COLOR: Record<Recency, string> = {
  fresh: COLORS.success,
  recent: COLORS.textSecondary,
  stale: COLORS.warning,
  cold: COLORS.border,
};

interface TimestampBadgeProps {
  minutesAgo: number;
}

export const TimestampBadge: React.FC<TimestampBadgeProps> = ({ minutesAgo }) => {
  const recency = recencyOf(minutesAgo);
  const color = RECENCY_COLOR[recency];
  const label = relativeTime(minutesAgo);

  return (
    <span
      style={{
        fontFamily: FONTS.mono,
        fontSize: 11,
        color,
        whiteSpace: "nowrap",
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
      }}
    >
      <span
        style={{
          width: 5,
          height: 5,
          borderRadius: "50%",
          background: color,
          display: "inline-block",
          flexShrink: 0,
        }}
      />
      {label}
    </span>
  );
};
