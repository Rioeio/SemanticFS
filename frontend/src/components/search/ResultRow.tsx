import React, { useRef, useEffect } from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import { highlightTerms } from "../../utils/format";
import { FileIcon } from "./FileIcon";
import { ScoreChip } from "./ScoreChip";
import { TimestampBadge } from "./TimestampBadge";
import type { Result } from "../../types/search";

export interface ResultRowProps {
  result: Result;
  terms: string[];
  selected: boolean;
  onSelect: () => void;
  onOpen: () => void;
}

export const ResultRow: React.FC<ResultRowProps> = ({
  result,
  terms,
  selected,
  onSelect,
  onOpen,
}) => {
  const rowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (selected) {
      rowRef.current?.scrollIntoView({ block: "nearest" });
    }
  }, [selected]);

  return (
    <div
      ref={rowRef}
      role="option"
      aria-selected={selected}
      onClick={onOpen}
      onMouseEnter={onSelect}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "10px 16px",
        background: selected ? `${COLORS.accent}12` : "transparent",
        borderLeft: `2px solid ${selected ? COLORS.accent : "transparent"}`,
        cursor: "pointer",
        transition: "background 60ms ease",
      }}
    >
      <FileIcon ext={result.ext} />
      <div
        style={{
          flex: 1,
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          gap: 3,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            gap: 8,
            overflow: "hidden",
          }}
        >
          <span
            style={{
              fontFamily: FONTS.sans,
              fontSize: 14,
              fontWeight: 600,
              color: COLORS.textPrimary,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              flexShrink: 0,
              maxWidth: 260,
            }}
          >
            {result.fileName}
          </span>
          <span
            style={{
              fontFamily: FONTS.mono,
              fontSize: 11,
              color: COLORS.textSecondary,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              minWidth: 0,
            }}
          >
            {result.folder}
          </span>
        </div>
        <span
          style={{
            fontFamily: FONTS.sans,
            fontSize: 12,
            color: COLORS.textSecondary,
            lineHeight: 1.5,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {highlightTerms(result.snippet, terms)}
        </span>
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-end",
          gap: 6,
          flexShrink: 0,
        }}
      >
        <ScoreChip score={result.score} />
        <TimestampBadge minutesAgo={result.minutesAgo} />
      </div>
    </div>
  );
};
