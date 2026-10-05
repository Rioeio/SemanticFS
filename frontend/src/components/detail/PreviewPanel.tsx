import React, { useState } from "react";
import { COLORS, EXT_COLORS, FONTS } from "../../tokens/design-tokens";
import { FileIcon } from "../search/FileIcon";
import { TimestampBadge } from "../search/TimestampBadge";
import { CodeBlock } from "./CodeBlock";
import { PlainBlock } from "./PlainBlock";
import { CitationRow } from "./CitationRow";
import { MetaChip } from "./MetaChip";
import { ActionButton } from "./ActionButton";
import type { Result } from "../../types/search";

export interface PreviewPanelProps {
  result: Result;
  terms: string[];
  onClose: () => void;
  onOpenInExplorer?: (path: string) => void;
}

export const PreviewPanel: React.FC<PreviewPanelProps> = ({
  result,
  terms,
  onClose,
  onOpenInExplorer,
}) => {
  const [copied, setCopied] = useState(false);
  const isCode = ["py", "js", "ts", "tsx", "json", "csv"].includes(result.ext);
  const color = EXT_COLORS[result.ext] ?? COLORS.textSecondary;

  function fmtBytes(b: number) {
    if (b < 1024) return `${b} B`;
    if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
    return `${(b / 1024 / 1024).toFixed(1)} MB`;
  }

  const fullPath = `${result.folder}/${result.fileName}`;

  const handleCopyPath = () => {
    if (navigator?.clipboard) {
      navigator.clipboard.writeText(fullPath);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleOpen = () => {
    if (onOpenInExplorer) {
      onOpenInExplorer(fullPath);
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0,0,0,0.55)",
          zIndex: 40,
          backdropFilter: "blur(3px)",
        }}
      />

      {/* Sheet Drawer */}
      <div
        role="dialog"
        aria-label={`Preview: ${result.fileName}`}
        style={{
          position: "fixed",
          top: 0,
          right: 0,
          bottom: 0,
          width: "min(680px, 90vw)",
          background: COLORS.surface,
          borderLeft: `1px solid ${COLORS.border}`,
          zIndex: 50,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* ── Header ── */}
        <div
          style={{
            padding: "16px 20px",
            borderBottom: `1px solid ${COLORS.border}`,
            display: "flex",
            flexDirection: "column",
            gap: 10,
            flexShrink: 0,
          }}
        >
          {/* Top row: icon + name + close */}
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <FileIcon ext={result.ext} />
            <div
              style={{
                flex: 1,
                minWidth: 0,
                display: "flex",
                flexDirection: "column",
                gap: 2,
              }}
            >
              <span
                style={{
                  fontFamily: FONTS.sans,
                  fontSize: 16,
                  fontWeight: 700,
                  color: COLORS.textPrimary,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
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
                }}
              >
                {fullPath}
              </span>
            </div>
            <button
              onClick={onClose}
              aria-label="Close preview"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 28,
                height: 28,
                borderRadius: 6,
                border: `1px solid ${COLORS.border}`,
                background: "transparent",
                color: COLORS.textSecondary,
                cursor: "pointer",
                flexShrink: 0,
                fontSize: 16,
                lineHeight: 1,
                transition: "background 80ms ease, color 80ms ease",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = COLORS.border;
                (e.currentTarget as HTMLButtonElement).style.color = COLORS.textPrimary;
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = "transparent";
                (e.currentTarget as HTMLButtonElement).style.color = COLORS.textSecondary;
              }}
            >
              ×
            </button>
          </div>

          {/* Meta row */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              flexWrap: "wrap",
            }}
          >
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 4,
                padding: "2px 8px",
                borderRadius: 4,
                background: `${color}14`,
                border: `1px solid ${color}30`,
                fontFamily: FONTS.mono,
                fontSize: 11,
                color,
              }}
            >
              .{result.ext}
            </span>
            {result.sizeBytes !== undefined && (
              <MetaChip label={fmtBytes(result.sizeBytes)} />
            )}
            {result.lineCount !== undefined && (
              <MetaChip label={`${result.lineCount} lines`} />
            )}
            <TimestampBadge minutesAgo={result.minutesAgo} />
            <span
              style={{
                fontFamily: FONTS.mono,
                fontSize: 11,
                color: COLORS.accent,
                marginLeft: "auto",
              }}
            >
              {Math.round(result.score * 100)}% match
            </span>
          </div>

          {/* Experimental label */}
          {result.experimental && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "8px 12px",
                background: `${COLORS.warning}0E`,
                border: `1px solid ${COLORS.warning}35`,
                borderRadius: 6,
              }}
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden>
                <path
                  d="M5.5 2h3l1 5H4.5l1-5z"
                  stroke={COLORS.warning}
                  strokeWidth="1.1"
                  strokeLinejoin="round"
                  fill={`${COLORS.warning}20`}
                />
                <path
                  d="M3.5 7c-.83.5-1.5 1.5-1.5 2.5C2 11.4 3.6 13 7 13s5-1.6 5-3.5c0-1-.67-2-1.5-2.5"
                  stroke={COLORS.warning}
                  strokeWidth="1.1"
                  strokeLinecap="round"
                />
                <circle cx="7" cy="10" r="1" fill={COLORS.warning} />
              </svg>
              <span style={{ flex: 1 }}>
                <span
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 11,
                    fontWeight: 600,
                    color: COLORS.warning,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                  }}
                >
                  {result.experimental.feature}
                </span>
                <span
                  style={{
                    fontFamily: FONTS.sans,
                    fontSize: 12,
                    color: COLORS.textSecondary,
                    marginLeft: 8,
                  }}
                >
                  {result.experimental.label}
                </span>
              </span>
            </div>
          )}
        </div>

        {/* ── Citations ── */}
        {result.citations && result.citations.length > 0 && (
          <div
            style={{
              padding: "12px 20px",
              borderBottom: `1px solid ${COLORS.border}`,
              display: "flex",
              flexDirection: "column",
              gap: 6,
              flexShrink: 0,
            }}
          >
            <span
              style={{
                fontFamily: FONTS.mono,
                fontSize: 10,
                fontWeight: 600,
                color: COLORS.textSecondary,
                letterSpacing: "0.1em",
                textTransform: "uppercase",
              }}
            >
              Why this matched
            </span>
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {result.citations.map((c, i) => (
                <CitationRow key={i} citation={c} />
              ))}
            </div>
          </div>
        )}

        {/* ── Content ── */}
        <div style={{ flex: 1, overflowY: "auto", padding: "16px 0" }}>
          {result.fullContent ? (
            isCode ? (
              <CodeBlock content={result.fullContent} ext={result.ext} terms={terms} />
            ) : (
              <PlainBlock content={result.fullContent} terms={terms} highlight />
            )
          ) : (
            <div style={{ padding: "0 20px" }}>
              <PlainBlock content={result.snippet} terms={terms} highlight />
            </div>
          )}
        </div>

        {/* ── Footer actions ── */}
        <div
          style={{
            padding: "12px 20px",
            borderTop: `1px solid ${COLORS.border}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexShrink: 0,
          }}
        >
          <span
            style={{
              fontFamily: FONTS.mono,
              fontSize: 11,
              color: COLORS.textSecondary,
              opacity: 0.5,
            }}
          >
            preview only · file unchanged
          </span>
          <div style={{ display: "flex", gap: 8 }}>
            <ActionButton
              label={copied ? "Copied!" : "Copy path"}
              onClick={handleCopyPath}
            />
            <ActionButton
              label="Open in Explorer"
              onClick={handleOpen}
              primary
            />
          </div>
        </div>
      </div>
    </>
  );
};
