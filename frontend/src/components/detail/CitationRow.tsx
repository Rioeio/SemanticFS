import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import type { MatchCitation, MatchSource } from "../../types/search";

export const SOURCE_LABEL: Record<MatchSource, string> = {
  body: "body text",
  filename: "filename",
  metadata: "metadata",
  ocr: "OCR extraction",
  vision: "vision inference",
};

export interface CitationRowProps {
  citation: MatchCitation;
}

export const CitationRow: React.FC<CitationRowProps> = ({ citation }) => {
  const confPct = Math.round(citation.confidence * 100);
  const barWidth = citation.confidence * 100;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "6px 10px",
        borderRadius: 6,
        background: COLORS.base,
        border: `1px solid ${COLORS.border}`,
      }}
    >
      {/* Term */}
      <span
        style={{
          fontFamily: FONTS.mono,
          fontSize: 12,
          color: COLORS.highlight,
          flexShrink: 0,
        }}
      >
        "{citation.term}"
      </span>

      {/* Source */}
      <span
        style={{
          fontFamily: FONTS.sans,
          fontSize: 12,
          color: COLORS.textSecondary,
          flexShrink: 0,
        }}
      >
        in {SOURCE_LABEL[citation.source] ?? citation.source}
        {citation.lineNo !== undefined && (
          <span
            style={{
              fontFamily: FONTS.mono,
              fontSize: 11,
              color: COLORS.textSecondary,
              opacity: 0.6,
              marginLeft: 4,
            }}
          >
            line {citation.lineNo}
          </span>
        )}
      </span>

      {/* Confidence bar */}
      <div
        style={{
          flex: 1,
          height: 3,
          background: COLORS.border,
          borderRadius: 2,
          overflow: "hidden",
          minWidth: 40,
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${barWidth}%`,
            background:
              citation.confidence > 0.85
                ? COLORS.success
                : citation.confidence > 0.65
                ? COLORS.accent
                : COLORS.warning,
            borderRadius: 2,
          }}
        />
      </div>

      {/* Confidence pct */}
      <span
        style={{
          fontFamily: FONTS.mono,
          fontSize: 11,
          color: COLORS.textSecondary,
          flexShrink: 0,
        }}
      >
        {confPct}%
      </span>
    </div>
  );
};
