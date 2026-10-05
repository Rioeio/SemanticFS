import React from "react";
import { COLORS } from "../tokens/design-tokens";
import type { Recency } from "../types/search";

export function highlightTerms(text: string, terms: string[]): React.ReactNode {
  const clean = terms.filter(Boolean);
  if (!clean.length) return text;
  
  const pattern = new RegExp(
    `(${clean.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`,
    "gi"
  );
  const parts = text.split(pattern);

  return (
    <>
      {parts.map((part, i) =>
        clean.some((t) => t.toLowerCase() === part.toLowerCase()) ? (
          <mark
            key={i}
            style={{
              background: `${COLORS.highlight}28`,
              color: COLORS.highlight,
              borderRadius: 2,
              padding: "0 2px",
              fontStyle: "normal",
            }}
          >
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

export function fmtNum(n: number): string {
  return n.toLocaleString("en-US");
}

export function recencyOf(minutesAgo: number): Recency {
  if (minutesAgo < 60) return "fresh";
  if (minutesAgo < 60 * 24) return "recent";
  if (minutesAgo < 60 * 24 * 7) return "stale";
  return "cold";
}

export function relativeTime(minutesAgo: number): string {
  if (minutesAgo < 1) return "just now";
  if (minutesAgo === 1) return "1m ago";
  if (minutesAgo < 60) return `${minutesAgo}m ago`;
  const hours = Math.floor(minutesAgo / 60);
  if (hours === 1) return "1h ago";
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return "1d ago";
  return `${days}d ago`;
}
