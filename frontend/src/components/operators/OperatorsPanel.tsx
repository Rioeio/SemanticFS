import React, { useState } from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import { OperatorRow } from "./OperatorRow";
import { OperatorExample } from "./OperatorExample";

export interface OperatorDefinition {
  op: string;
  desc: string;
}

export const OPERATORS: OperatorDefinition[] = [
  { op: "ext:pdf", desc: "filter by file type" },
  { op: "+budget", desc: "must include term" },
  { op: "-node_modules", desc: "exclude term" },
  { op: "score:>0.8", desc: "minimum match score" },
  { op: "modified:<7d", desc: "recency filter" },
  { op: "in:~/Documents", desc: "scope to folder" },
];

export interface OperatorsPanelProps {
  collapsible?: boolean;
  defaultOpen?: boolean;
  onSelectOperator?: (op: string) => void;
  onSelectExample?: (example: string) => void;
  operators?: OperatorDefinition[];
}

export const OperatorsPanel: React.FC<OperatorsPanelProps> = ({
  collapsible = true,
  defaultOpen = false,
  onSelectOperator,
  onSelectExample,
  operators = OPERATORS,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const content = (
    <div
      style={{
        marginTop: collapsible ? 12 : 0,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <p
        style={{
          fontFamily: FONTS.sans,
          fontSize: 12,
          color: COLORS.textSecondary,
          margin: "0 0 8px",
          lineHeight: 1.5,
        }}
      >
        Combine operators with natural language. Separate with spaces.
      </p>

      {operators.map(({ op, desc }) => (
        <OperatorRow
          key={op}
          op={op}
          desc={desc}
          onClick={onSelectOperator}
        />
      ))}

      <OperatorExample onSelectExample={onSelectExample} />
    </div>
  );

  if (!collapsible) {
    return content;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
      <button
        onClick={() => setIsOpen((v) => !v)}
        aria-expanded={isOpen}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "none",
          border: "none",
          cursor: "pointer",
          padding: "4px 0",
          width: "100%",
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
          Advanced
        </span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          aria-hidden
          style={{
            color: COLORS.textSecondary,
            transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 150ms ease",
          }}
        >
          <path
            d="M2 4l4 4 4-4"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && content}
    </div>
  );
};
