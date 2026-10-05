import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import { fmtNum } from "../../utils/format";

export interface IndexingProgressProps {
  isIndexing: boolean;
  indexedCount: number;
  totalFiles: number;
  daemonPid?: number;
}

export const IndexingProgress: React.FC<IndexingProgressProps> = ({
  isIndexing,
  indexedCount,
  totalFiles,
  daemonPid = 48291,
}) => {
  const progressPct = Math.round((indexedCount / totalFiles) * 100);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {isIndexing && (
        <div
          style={{
            padding: "12px 14px",
            background: COLORS.base,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 8,
            display: "flex",
            flexDirection: "column",
            gap: 8,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <span
              style={{
                fontFamily: FONTS.sans,
                fontSize: 12,
                color: COLORS.textPrimary,
              }}
            >
              Indexing in progress
            </span>
            <span
              style={{
                fontFamily: FONTS.mono,
                fontSize: 11,
                color: COLORS.warning,
              }}
            >
              {progressPct}%
            </span>
          </div>

          {/* Progress bar track & fill */}
          <div
            style={{
              height: 3,
              borderRadius: 2,
              background: COLORS.border,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${progressPct}%`,
                background: COLORS.warning,
                borderRadius: 2,
                transition: "width 400ms linear",
              }}
            />
          </div>

          {/* File counts */}
          <span
            style={{
              fontFamily: FONTS.mono,
              fontSize: 11,
              color: COLORS.textSecondary,
            }}
          >
            Indexing{" "}
            <span style={{ color: COLORS.textPrimary }}>{fmtNum(indexedCount)}</span>
            {" / "}
            <span style={{ color: COLORS.textPrimary }}>{fmtNum(totalFiles)}</span>
            {" files"}
          </span>
        </div>
      )}

      {/* Live daemon status indicator */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          fontFamily: FONTS.mono,
          fontSize: 11,
          color: COLORS.textSecondary,
        }}
      >
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            background: COLORS.success,
            boxShadow: `0 0 0 3px ${COLORS.success}30`,
          }}
        />
        daemon running · pid {daemonPid}
      </div>
    </div>
  );
};
