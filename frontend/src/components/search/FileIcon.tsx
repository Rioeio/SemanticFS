import React from "react";
import { EXT_COLORS, COLORS, FONTS } from "../../tokens/design-tokens";

interface FileIconProps {
  ext: string;
}

export const FileIcon: React.FC<FileIconProps> = ({ ext }) => {
  const color = EXT_COLORS[ext] ?? COLORS.textSecondary;
  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden
      style={{ flexShrink: 0 }}
    >
      <rect
        x="6"
        y="3"
        width="16"
        height="20"
        rx="2"
        fill={`${color}18`}
        stroke={`${color}50`}
        strokeWidth="1"
      />
      <path
        d="M18 3v5h4"
        stroke={`${color}50`}
        strokeWidth="1"
        fill="none"
      />
      <text
        x="14"
        y="19"
        textAnchor="middle"
        fill={color}
        fontFamily={FONTS.mono}
        fontSize="5.5"
        fontWeight="600"
        letterSpacing="0.02em"
      >
        {ext.toUpperCase().slice(0, 3)}
      </text>
    </svg>
  );
};
