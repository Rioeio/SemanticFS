import React, { useState } from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

export interface SearchInputProps {
  value: string;
  onChange: (v: string) => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  latencyMs: number | null;
  hasResults: boolean;
  inputRef: React.RefObject<HTMLInputElement | null>;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  value,
  onChange,
  onKeyDown,
  latencyMs,
  hasResults,
  inputRef,
}) => {
  const [focused, setFocused] = useState(true);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        height: 52,
        padding: "0 16px",
        background: COLORS.surface,
        border: `1px solid ${focused ? COLORS.accent : COLORS.border}`,
        borderRadius: value && hasResults ? "10px 10px 0 0" : 10,
        boxShadow: focused ? `0 0 0 3px ${COLORS.accent}1A` : "none",
        transition:
          "border-color 100ms ease, box-shadow 100ms ease, border-radius 80ms ease",
      }}
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        aria-hidden
        style={{ flexShrink: 0 }}
      >
        <circle
          cx="6.5"
          cy="6.5"
          r="4.5"
          stroke={focused ? COLORS.accent : COLORS.textSecondary}
          strokeWidth="1.25"
          style={{ transition: "stroke 100ms" }}
        />
        <path
          d="M10.5 10.5L13.5 13.5"
          stroke={focused ? COLORS.accent : COLORS.textSecondary}
          strokeWidth="1.25"
          strokeLinecap="round"
          style={{ transition: "stroke 100ms" }}
        />
      </svg>
      <input
        ref={inputRef}
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder="Search your files by meaning…"
        aria-label="Semantic file search"
        autoFocus
        style={{
          flex: 1,
          background: "none",
          border: "none",
          outline: "none",
          color: COLORS.textPrimary,
          fontFamily: FONTS.sans,
          fontSize: 16,
          lineHeight: 1.4,
          caretColor: COLORS.accent,
        }}
      />
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
        {latencyMs !== null && (
          <span
            style={{
              fontFamily: FONTS.mono,
              fontSize: 11,
              color: COLORS.textSecondary,
              opacity: 0.7,
            }}
          >
            {latencyMs}ms
          </span>
        )}
        <kbd
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            height: 20,
            padding: "0 6px",
            borderRadius: 4,
            border: `1px solid ${COLORS.border}`,
            background: COLORS.base,
            color: COLORS.textSecondary,
            fontFamily: FONTS.mono,
            fontSize: 11,
            userSelect: "none",
          }}
        >
          esc
        </kbd>
      </div>
    </div>
  );
};
