import React, { useRef, useEffect } from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import { SearchInput } from "./SearchInput";
import { ResultRow } from "./ResultRow";
import { EmptyState } from "./EmptyState";
import { FooterKbd } from "./FooterKbd";
import type { Result } from "../../types/search";

export interface SearchScreenProps {
  query: string;
  onQueryChange: (q: string) => void;
  results: Result[];
  selectedIdx: number;
  onSelectIdx: (idx: number) => void;
  latencyMs: number | null;
  isIndexing: boolean;
  onOpenSettings: () => void;
  onOpenResult: (result: Result) => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
}

export const SearchScreen: React.FC<SearchScreenProps> = ({
  query,
  onQueryChange,
  results,
  selectedIdx,
  onSelectIdx,
  latencyMs,
  isIndexing,
  onOpenSettings,
  onOpenResult,
  onKeyDown,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const terms = query.trim().split(/\s+/).filter(Boolean);
  const showResults = query.trim().length > 0;

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <div
      onKeyDown={onKeyDown}
      style={{
        minHeight: "100%",
        background: COLORS.base,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "80px 24px 48px",
      }}
    >
      {/* Wordmark + settings trigger */}
      <div
        style={{
          marginBottom: 32,
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <span
          style={{
            fontFamily: FONTS.mono,
            fontSize: 14,
            fontWeight: 600,
            color: COLORS.textSecondary,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
          }}
        >
          Semantic<span style={{ color: COLORS.accent }}>FS</span>
        </span>

        {/* Indexing pulse — shown when daemon is active */}
        {isIndexing && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 5,
              padding: "3px 8px",
              borderRadius: 20,
              background: `${COLORS.warning}12`,
              border: `1px solid ${COLORS.warning}30`,
            }}
          >
            <span
              style={{
                width: 5,
                height: 5,
                borderRadius: "50%",
                background: COLORS.warning,
                animation: "pulse 1.4s ease-in-out infinite",
              }}
            />
            <span
              style={{
                fontFamily: FONTS.mono,
                fontSize: 10,
                color: COLORS.warning,
                whiteSpace: "nowrap",
              }}
            >
              indexing
            </span>
          </div>
        )}

        {/* Settings gear */}
        <button
          onClick={onOpenSettings}
          aria-label="Open settings (⌘,)"
          title="Settings (⌘,)"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 28,
            height: 28,
            borderRadius: 6,
            background: "none",
            border: `1px solid ${COLORS.border}`,
            color: COLORS.textSecondary,
            cursor: "pointer",
            transition: "border-color 80ms, color 80ms",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = COLORS.accent;
            (e.currentTarget as HTMLButtonElement).style.color = COLORS.accent;
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = COLORS.border;
            (e.currentTarget as HTMLButtonElement).style.color = COLORS.textSecondary;
          }}
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden>
            <circle cx="7" cy="7" r="2" stroke="currentColor" strokeWidth="1.2" />
            <path
              d="M7 1v1.5M7 11.5V13M1 7h1.5M11.5 7H13M2.93 2.93l1.06 1.06M10.01 10.01l1.06 1.06M2.93 11.07l1.06-1.06M10.01 3.99l1.06-1.06"
              stroke="currentColor"
              strokeWidth="1.2"
              strokeLinecap="round"
            />
          </svg>
        </button>
      </div>

      {/* Palette container */}
      <div
        role="combobox"
        aria-expanded={showResults}
        aria-haspopup="listbox"
        style={{
          width: "100%",
          maxWidth: 640,
          borderRadius: 10,
          boxShadow: showResults
            ? `0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px ${COLORS.border}`
            : `0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px ${COLORS.border}`,
          transition: "box-shadow 200ms ease",
          overflow: "hidden",
        }}
      >
        <SearchInput
          value={query}
          onChange={onQueryChange}
          onKeyDown={onKeyDown}
          latencyMs={latencyMs}
          hasResults={showResults && results.length > 0}
          inputRef={inputRef}
        />

        {showResults && (
          <div
            role="listbox"
            aria-label="Search results"
            style={{
              background: COLORS.surface,
              borderTop: `1px solid ${COLORS.border}`,
              maxHeight: 440,
              overflowY: "auto",
            }}
          >
            {results.length === 0 ? (
              <EmptyState query={query} />
            ) : (
              <>
                {results.map((r, i) => (
                  <ResultRow
                    key={r.id}
                    result={r}
                    terms={terms}
                    selected={i === selectedIdx}
                    onSelect={() => onSelectIdx(i)}
                    onOpen={() => onOpenResult(r)}
                  />
                ))}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "8px 16px",
                    borderTop: `1px solid ${COLORS.border}`,
                  }}
                >
                  <span
                    style={{
                      fontFamily: FONTS.mono,
                      fontSize: 11,
                      color: COLORS.textSecondary,
                      opacity: 0.6,
                    }}
                  >
                    {results.length} result{results.length !== 1 ? "s" : ""} · local only
                  </span>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <FooterKbd keys={["↑", "↓"]} label="navigate" />
                    <FooterKbd keys={["↵"]} label="open" />
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Idle hint */}
      {!showResults && (
        <p
          style={{
            marginTop: 16,
            fontFamily: FONTS.sans,
            fontSize: 13,
            color: COLORS.textSecondary,
            opacity: 0.6,
            textAlign: "center",
          }}
        >
          Press{" "}
          <kbd
            style={{
              fontFamily: FONTS.mono,
              fontSize: 11,
              color: COLORS.textSecondary,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 4,
              padding: "1px 5px",
              background: COLORS.surface,
            }}
          >
            /
          </kbd>{" "}
          to search · all search runs on your device
        </p>
      )}
    </div>
  );
};
