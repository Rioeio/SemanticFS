import React, { useState, useEffect } from "react";
import { COLORS, FONTS } from "../../tokens/design-tokens";
import { fmtNum } from "../../utils/format";
import { PrivacyBadge } from "./PrivacyBadge";
import { StatTile } from "./StatTile";
import { IndexingProgress } from "./IndexingProgress";
import { WatchedFoldersList } from "./WatchedFoldersList";
import { OperatorsPanel, OPERATORS } from "../operators/OperatorsPanel";
import type { WatchedFolder } from "../../types/status";

export { OPERATORS };

export const INITIAL_FOLDERS: WatchedFolder[] = [
  { id: "f1", path: "~/Documents", fileCount: 1842 },
  { id: "f2", path: "~/Projects", fileCount: 1104 },
  { id: "f3", path: "~/Research", fileCount: 431 },
  { id: "f4", path: "~/Desktop", fileCount: 38 },
];

export interface StatusPanelProps {
  onClose: () => void;
  initialFolders?: WatchedFolder[];
  onSelectOperator?: (op: string) => void;
  onSelectExample?: (example: string) => void;
}

export const StatusPanel: React.FC<StatusPanelProps> = ({
  onClose,
  initialFolders = INITIAL_FOLDERS,
  onSelectOperator,
  onSelectExample,
}) => {
  const TOTAL_FILES = 3800;
  const [indexedCount, setIndexedCount] = useState(1204);
  const [isIndexing] = useState(true);
  const [folders, setFolders] = useState<WatchedFolder[]>(initialFolders);

  // Simulate live indexing progress
  useEffect(() => {
    if (!isIndexing) return;
    const interval = setInterval(() => {
      setIndexedCount((n) => {
        const next = n + Math.floor(Math.random() * 7 + 2);
        return Math.min(next, TOTAL_FILES);
      });
    }, 400);
    return () => clearInterval(interval);
  }, [isIndexing]);

  const totalIndexed = folders.reduce((s, f) => s + f.fileCount, 0);

  const handleAddFolder = (path: string) => {
    setFolders((fs) => [...fs, { id: `f${Date.now()}`, path, fileCount: 0 }]);
  };

  const handleEditFolder = (id: string, newPath: string) => {
    setFolders((fs) =>
      fs.map((f) => (f.id === id ? { ...f, path: newPath } : f))
    );
  };

  const handleRemoveFolder = (id: string) => {
    setFolders((fs) => fs.filter((f) => f.id !== id));
  };

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0,0,0,0.5)",
          zIndex: 40,
          backdropFilter: "blur(2px)",
        }}
      />

      {/* Drawer Panel */}
      <div
        role="dialog"
        aria-label="Index status and settings"
        style={{
          position: "fixed",
          top: 0,
          right: 0,
          bottom: 0,
          width: 360,
          background: COLORS.surface,
          borderLeft: `1px solid ${COLORS.border}`,
          zIndex: 50,
          display: "flex",
          flexDirection: "column",
          overflowY: "auto",
        }}
      >
        {/* Panel header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "16px 20px",
            borderBottom: `1px solid ${COLORS.border}`,
            position: "sticky",
            top: 0,
            background: COLORS.surface,
            zIndex: 1,
          }}
        >
          <span
            style={{
              fontFamily: FONTS.sans,
              fontSize: 14,
              fontWeight: 600,
              color: COLORS.textPrimary,
            }}
          >
            Index &amp; Settings
          </span>
          <button
            onClick={onClose}
            aria-label="Close panel"
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
              fontFamily: FONTS.mono,
              fontSize: 14,
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

        {/* Body */}
        <div
          style={{
            flex: 1,
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            gap: 24,
          }}
        >
          {/* Privacy badge */}
          <PrivacyBadge />

          {/* Index stats */}
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
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
              Index
            </span>

            {/* Stat row */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 8,
              }}
            >
              <StatTile label="Files indexed" value={fmtNum(totalIndexed)} />
              <StatTile label="Watched folders" value={String(folders.length)} />
            </div>

            {/* Indexing progress & live daemon indicator */}
            <IndexingProgress
              isIndexing={isIndexing}
              indexedCount={indexedCount}
              totalFiles={TOTAL_FILES}
            />
          </div>

          <div style={{ height: 1, background: COLORS.border, margin: "4px 0" }} />

          {/* Watched folders */}
          <WatchedFoldersList
            folders={folders}
            onAddFolder={handleAddFolder}
            onEditFolder={handleEditFolder}
            onRemoveFolder={handleRemoveFolder}
          />

          <div style={{ height: 1, background: COLORS.border, margin: "4px 0" }} />

          {/* Advanced operators panel */}
          <OperatorsPanel
            onSelectOperator={onSelectOperator}
            onSelectExample={onSelectExample}
          />

          {/* Bottom spacer */}
          <div style={{ flex: 1 }} />

          {/* Footer */}
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 10,
              color: COLORS.textSecondary,
              opacity: 0.5,
              lineHeight: 1.6,
            }}
          >
            SemanticFS v0.9.4 · nomic-embed-text-v1.5
            <br />
            index at ~/.semanticfs/index.db
          </div>
        </div>
      </div>
    </>
  );
};
