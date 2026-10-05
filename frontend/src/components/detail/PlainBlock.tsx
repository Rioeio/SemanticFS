import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import { highlightTerms } from "../../utils/format";

export interface PlainBlockProps {
  content: string;
  terms: string[];
  highlight: boolean;
}

export const PlainBlock: React.FC<PlainBlockProps> = ({ content, terms, highlight }) => {
  const lines = content.split("\n");

  return (
    <div>
      {lines.map((line, i) => {
        const hasMatch =
          highlight && terms.some((t) => line.toLowerCase().includes(t.toLowerCase()));
        return (
          <div
            key={i}
            style={{
              fontFamily: FONTS.sans,
              fontSize: 13,
              lineHeight: "22px",
              color: COLORS.textPrimary,
              padding: "0 20px",
              background: hasMatch ? `${COLORS.highlight}08` : "transparent",
              borderLeft: hasMatch
                ? `2px solid ${COLORS.highlight}60`
                : "2px solid transparent",
            }}
          >
            {line ? highlightTerms(line, terms) : <br />}
          </div>
        );
      })}
    </div>
  );
};
