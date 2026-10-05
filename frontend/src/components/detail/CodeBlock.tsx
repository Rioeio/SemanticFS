import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";

type TokenKind = "keyword" | "string" | "comment" | "number" | "operator" | "plain";
export type Token = { kind: TokenKind; text: string };

const PY_KEYWORDS = new Set([
  "def", "class", "import", "from", "return", "if", "else", "elif",
  "for", "while", "in", "not", "and", "or", "True", "False", "None",
  "with", "as", "try", "except", "raise", "lambda", "yield", "pass",
  "break", "continue", "global", "nonlocal", "async", "await",
]);

const JS_KEYWORDS = new Set([
  "const", "let", "var", "function", "return", "if", "else", "for",
  "while", "import", "export", "default", "from", "class", "extends",
  "new", "typeof", "instanceof", "null", "undefined", "true", "false",
  "async", "await", "of", "in", "throw", "try", "catch", "finally",
  "interface", "type", "enum",
]);

export function tokenizePy(line: string): Token[] {
  const out: Token[] = [];
  let i = 0;
  while (i < line.length) {
    if (line[i] === "#") {
      out.push({ kind: "comment", text: line.slice(i) });
      break;
    }
    const strMatch = line.slice(i).match(/^("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/);
    if (strMatch) {
      out.push({ kind: "string", text: strMatch[0] });
      i += strMatch[0].length;
      continue;
    }
    const numMatch = line.slice(i).match(/^\d[\d_.]*/);
    if (numMatch) {
      out.push({ kind: "number", text: numMatch[0] });
      i += numMatch[0].length;
      continue;
    }
    const wordMatch = line.slice(i).match(/^[A-Za-z_]\w*/);
    if (wordMatch) {
      const w = wordMatch[0];
      out.push({ kind: PY_KEYWORDS.has(w) ? "keyword" : "plain", text: w });
      i += w.length;
      continue;
    }
    const opMatch = line.slice(i).match(/^[=<>!+\-*/%&|^~:.,()[\]{}]+/);
    if (opMatch) {
      out.push({ kind: "operator", text: opMatch[0] });
      i += opMatch[0].length;
      continue;
    }
    out.push({ kind: "plain", text: line[i] });
    i++;
  }
  return out;
}

export function tokenizeJs(line: string): Token[] {
  const out: Token[] = [];
  let i = 0;
  while (i < line.length) {
    if (line.slice(i, i + 2) === "//") {
      out.push({ kind: "comment", text: line.slice(i) });
      break;
    }
    const strMatch = line.slice(i).match(/^(`[^`]*`|"[^"]*"|'[^']*')/);
    if (strMatch) {
      out.push({ kind: "string", text: strMatch[0] });
      i += strMatch[0].length;
      continue;
    }
    const numMatch = line.slice(i).match(/^\d[\d.]*/);
    if (numMatch) {
      out.push({ kind: "number", text: numMatch[0] });
      i += numMatch[0].length;
      continue;
    }
    const wordMatch = line.slice(i).match(/^[A-Za-z_$]\w*/);
    if (wordMatch) {
      const w = wordMatch[0];
      out.push({ kind: JS_KEYWORDS.has(w) ? "keyword" : "plain", text: w });
      i += w.length;
      continue;
    }
    const opMatch = line.slice(i).match(/^[=<>!+\-*/%&|^~:.,()[\]{}]+/);
    if (opMatch) {
      out.push({ kind: "operator", text: opMatch[0] });
      i += opMatch[0].length;
      continue;
    }
    out.push({ kind: "plain", text: line[i] });
    i++;
  }
  return out;
}

export function tokenizeJson(line: string): Token[] {
  const out: Token[] = [];
  let i = 0;
  while (i < line.length) {
    const strMatch = line.slice(i).match(/^"[^"]*"/);
    if (strMatch) {
      const isKey = line.slice(i + strMatch[0].length).trimStart().startsWith(":");
      out.push({ kind: isKey ? "keyword" : "string", text: strMatch[0] });
      i += strMatch[0].length;
      continue;
    }
    const numMatch = line.slice(i).match(/^-?\d[\d.eE+-]*/);
    if (numMatch) {
      out.push({ kind: "number", text: numMatch[0] });
      i += numMatch[0].length;
      continue;
    }
    const boolMatch = line.slice(i).match(/^(true|false|null)/);
    if (boolMatch) {
      out.push({ kind: "operator", text: boolMatch[0] });
      i += boolMatch[0].length;
      continue;
    }
    out.push({ kind: "plain", text: line[i] });
    i++;
  }
  return out;
}

const TOKEN_COLOR: Record<TokenKind, string> = {
  keyword: COLORS.accent,
  string: COLORS.success,
  comment: COLORS.textSecondary,
  number: COLORS.warning,
  operator: COLORS.mono,
  plain: COLORS.textPrimary,
};

export interface SyntaxLineProps {
  line: string;
  ext: string;
  terms: string[];
  lineNo: number;
}

export const SyntaxLine: React.FC<SyntaxLineProps> = ({ line, ext, terms, lineNo }) => {
  const tokenize = ext === "py" ? tokenizePy : ext === "json" ? tokenizeJson : tokenizeJs;
  const tokens = ["py", "js", "ts", "tsx", "json"].includes(ext)
    ? tokenize(line)
    : [{ kind: "plain" as const, text: line }];

  const hasMatch = terms.some((t) => line.toLowerCase().includes(t.toLowerCase()));

  return (
    <div
      style={{
        display: "flex",
        background: hasMatch ? `${COLORS.highlight}08` : "transparent",
        borderLeft: hasMatch ? `2px solid ${COLORS.highlight}60` : "2px solid transparent",
      }}
    >
      <span
        style={{
          fontFamily: FONTS.mono,
          fontSize: 12,
          lineHeight: "20px",
          color: COLORS.textSecondary,
          opacity: 0.4,
          userSelect: "none",
          flexShrink: 0,
          width: 40,
          textAlign: "right",
          paddingRight: 16,
          paddingLeft: 8,
        }}
      >
        {lineNo}
      </span>
      <span
        style={{
          flex: 1,
          fontFamily: FONTS.mono,
          fontSize: 12,
          lineHeight: "20px",
          whiteSpace: "pre",
        }}
      >
        {tokens.map((tok, i) => {
          const color = TOKEN_COLOR[tok.kind];
          const termHit = terms.find((t) =>
            tok.text.toLowerCase().includes(t.toLowerCase())
          );
          if (termHit) {
            const parts = tok.text.split(
              new RegExp(`(${termHit.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi")
            );
            return (
              <span key={i} style={{ color }}>
                {parts.map((p, j) =>
                  p.toLowerCase() === termHit.toLowerCase() ? (
                    <mark
                      key={j}
                      style={{
                        background: `${COLORS.highlight}30`,
                        color: COLORS.highlight,
                        borderRadius: 2,
                      }}
                    >
                      {p}
                    </mark>
                  ) : (
                    p
                  )
                )}
              </span>
            );
          }
          return (
            <span key={i} style={{ color }}>
              {tok.text}
            </span>
          );
        })}
      </span>
    </div>
  );
};

export interface CodeBlockProps {
  content: string;
  ext: string;
  terms: string[];
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ content, ext, terms }) => {
  const lines = content.split("\n");
  const matchLines = new Set(
    lines
      .map((l, i) => ({ l, i }))
      .filter(({ l }) => terms.some((t) => l.toLowerCase().includes(t.toLowerCase())))
      .map(({ i }) => i)
  );

  // Show ±4 lines around each match, plus first 4 lines always
  const shown = new Set<number>();
  [0, 1, 2, 3].forEach((n) => {
    if (n < lines.length) shown.add(n);
  });
  matchLines.forEach((mi) => {
    for (let d = -4; d <= 4; d++) {
      const n = mi + d;
      if (n >= 0 && n < lines.length) shown.add(n);
    }
  });

  const sorted = [...shown].sort((a, b) => a - b);
  const blocks: number[][] = [];
  let cur: number[] = [];
  sorted.forEach((n, i) => {
    if (i === 0 || n !== sorted[i - 1] + 1) {
      if (cur.length) blocks.push(cur);
      cur = [];
    }
    cur.push(n);
  });
  if (cur.length) blocks.push(cur);

  return (
    <div style={{ overflowX: "auto" }}>
      {blocks.map((block, bi) => (
        <div key={bi}>
          {bi > 0 && (
            <div
              style={{
                fontFamily: FONTS.mono,
                fontSize: 11,
                color: COLORS.textSecondary,
                opacity: 0.4,
                padding: "2px 8px 2px 48px",
                userSelect: "none",
              }}
            >
              ⋯
            </div>
          )}
          {block.map((n) => (
            <SyntaxLine key={n} line={lines[n]} ext={ext} terms={terms} lineNo={n + 1} />
          ))}
        </div>
      ))}
    </div>
  );
};
