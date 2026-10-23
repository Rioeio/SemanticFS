import React from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import { fmtNum } from "../../utils/format";
import type { WatchedFolder } from "../../types/status";

export interface WatchedFoldersListProps {
  folders: WatchedFolder[];
}

export const WatchedFoldersList: React.FC<WatchedFoldersListProps> = ({
  folders,
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
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
          Watched Directories
        </span>
        <span
          style={{
            fontFamily: FONTS.mono,
            fontSize: 10,
            color: COLORS.textSecondary,
            opacity: 0.7,
          }}
        >
          Read-only
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {folders.length === 0 ? (
          <div
            style={{
              padding: "12px",
              borderRadius: 6,
              background: COLORS.base,
              border: `1px solid ${COLORS.border}`,
              color: COLORS.textSecondary,
              fontFamily: FONTS.sans,
              fontSize: 12,
              textAlign: "center",
            }}
          >
            No directories currently monitored
          </div>
        ) : (
          folders.map((f) => (
            <div
              key={f.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "8px 10px",
                borderRadius: 6,
                background: COLORS.base,
                border: `1px solid ${COLORS.border}`,
              }}
            >
              {/* Folder icon */}
              <svg
                width="14"
                height="14"
                viewBox="0 0 14 14"
                fill="none"
                aria-hidden
                style={{ flexShrink: 0 }}
              >
                <path
                  d="M1 3.5C1 2.67 1.67 2 2.5 2H5l1.5 1.5H11.5c.83 0 1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5h-9C1.67 11.5 1 10.83 1 10V3.5z"
                  fill={`${COLORS.mono}18`}
                  stroke={`${COLORS.mono}60`}
                  strokeWidth="1"
                />
              </svg>

              <span
                title={f.path}
                style={{
                  flex: 1,
                  minWidth: 0,
                  fontFamily: FONTS.mono,
                  fontSize: 12,
                  color: COLORS.textPrimary,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {f.path}
              </span>

              {f.exists === false && (
                <span
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 9,
                    color: COLORS.danger,
                    background: `${COLORS.danger}18`,
                    padding: "2px 5px",
                    borderRadius: 4,
                  }}
                >
                  missing
                </span>
              )}

              <span
                style={{
                  fontFamily: FONTS.mono,
                  fontSize: 10,
                  color: COLORS.textSecondary,
                  flexShrink: 0,
                }}
              >
                {fmtNum(f.fileCount)}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
