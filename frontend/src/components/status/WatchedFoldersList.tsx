import React, { useState } from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import { fmtNum } from "../../utils/format";
import type { WatchedFolder } from "../../types/status";

export interface WatchedFoldersListProps {
  folders: WatchedFolder[];
  onAddFolder: (path: string) => void;
  onEditFolder: (id: string, newPath: string) => void;
  onRemoveFolder: (id: string) => void;
}

export const WatchedFoldersList: React.FC<WatchedFoldersListProps> = ({
  folders,
  onAddFolder,
  onEditFolder,
  onRemoveFolder,
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [addingFolder, setAddingFolder] = useState(false);
  const [newFolderDraft, setNewFolderDraft] = useState("");

  const startEdit = (f: WatchedFolder) => {
    setEditingId(f.id);
    setEditValue(f.path);
  };

  const commitEdit = (id: string) => {
    const trimmed = editValue.trim();
    if (trimmed) {
      onEditFolder(id, trimmed);
    }
    setEditingId(null);
  };

  const handleAdd = () => {
    const trimmed = newFolderDraft.trim();
    if (trimmed) {
      onAddFolder(trimmed);
      setNewFolderDraft("");
      setAddingFolder(false);
    }
  };

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
          Watched Folders
        </span>
        <button
          onClick={() => setAddingFolder(true)}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            background: "none",
            border: "none",
            cursor: "pointer",
            color: COLORS.accent,
            fontFamily: FONTS.sans,
            fontSize: 12,
            fontWeight: 500,
            padding: 0,
          }}
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden>
            <path
              d="M6 1v10M1 6h10"
              stroke="currentColor"
              strokeWidth="1.25"
              strokeLinecap="round"
            />
          </svg>
          Add
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {folders.map((f) => (
          <div
            key={f.id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "8px 10px",
              borderRadius: 6,
              background: COLORS.base,
              border: `1px solid ${editingId === f.id ? COLORS.accent : COLORS.border}`,
              transition: "border-color 80ms ease",
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

            {editingId === f.id ? (
              <input
                autoFocus
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") commitEdit(f.id);
                  if (e.key === "Escape") setEditingId(null);
                }}
                onBlur={() => commitEdit(f.id)}
                style={{
                  flex: 1,
                  background: "none",
                  border: "none",
                  outline: "none",
                  color: COLORS.textPrimary,
                  fontFamily: FONTS.mono,
                  fontSize: 12,
                  caretColor: COLORS.accent,
                  minWidth: 0,
                }}
              />
            ) : (
              <span
                onClick={() => startEdit(f)}
                style={{
                  flex: 1,
                  minWidth: 0,
                  fontFamily: FONTS.mono,
                  fontSize: 12,
                  color: COLORS.textPrimary,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  cursor: "text",
                }}
              >
                {f.path}
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

            <button
              onClick={() => onRemoveFolder(f.id)}
              aria-label={`Remove ${f.path}`}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 20,
                height: 20,
                borderRadius: 4,
                background: "none",
                border: "none",
                color: COLORS.textSecondary,
                cursor: "pointer",
                flexShrink: 0,
                transition: "color 80ms ease",
              }}
              onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.color = COLORS.danger)}
              onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.color = COLORS.textSecondary)}
            >
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden>
                <path
                  d="M2 2l6 6M8 2L2 8"
                  stroke="currentColor"
                  strokeWidth="1.25"
                  strokeLinecap="round"
                />
              </svg>
            </button>
          </div>
        ))}

        {/* Add folder inline input */}
        {addingFolder && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "8px 10px",
              borderRadius: 6,
              background: COLORS.base,
              border: `1px solid ${COLORS.accent}`,
            }}
          >
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
                fill={`${COLORS.accent}18`}
                stroke={`${COLORS.accent}60`}
                strokeWidth="1"
              />
            </svg>
            <input
              autoFocus
              value={newFolderDraft}
              onChange={(e) => setNewFolderDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleAdd();
                if (e.key === "Escape") {
                  setAddingFolder(false);
                  setNewFolderDraft("");
                }
              }}
              placeholder="~/path/to/folder"
              style={{
                flex: 1,
                background: "none",
                border: "none",
                outline: "none",
                color: COLORS.textPrimary,
                fontFamily: FONTS.mono,
                fontSize: 12,
                caretColor: COLORS.accent,
              }}
            />
            <button
              onClick={handleAdd}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                color: COLORS.accent,
                fontFamily: FONTS.sans,
                fontSize: 11,
                padding: 0,
              }}
            >
              Add
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
