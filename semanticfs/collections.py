from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

COLLECTIONS_FILE = Path("~/.semanticfs/collections.json").expanduser()
VIRTUAL_DRIVE_DIR = Path("~/.semanticfs/virtual_drive").expanduser()

class CollectionManager:
    """Manages Virtual Smart Collections (Zero Disk Modification - Virtual Explorer Shortcuts)."""
    def __init__(self):
        COLLECTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.collections: dict[str, dict[str, Any]] = self._load()

    def _load(self) -> dict[str, dict[str, Any]]:
        if COLLECTIONS_FILE.exists():
            try:
                with open(COLLECTIONS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.debug(f"Failed to load collections: {e}")
        return {}

    def save(self) -> None:
        try:
            with open(COLLECTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.collections, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to save collections: {e}")

    def create_collection(self, name: str, query: str, matched_filepaths: list[str]) -> bool:
        """Create or update a virtual collection without modifying any real files on disk."""
        self.collections[name] = {
            "name": name,
            "query": query,
            "filepaths": matched_filepaths,
            "count": len(matched_filepaths)
        }
        self.save()
        self.sync_virtual_drive()
        return True

    def list_collections(self) -> list[dict[str, Any]]:
        return list(self.collections.values())

    def get_collection(self, name: str) -> dict[str, Any] | None:
        return self.collections.get(name)

    def delete_collection(self, name: str) -> bool:
        if name in self.collections:
            del self.collections[name]
            self.save()
            self.sync_virtual_drive()
            return True
        return False

    def sync_virtual_drive(self) -> None:
        """Populates Windows File Explorer virtual drive with shortcut files (.url/.lnk) without moving real files."""
        try:
            VIRTUAL_DRIVE_DIR.mkdir(parents=True, exist_ok=True)

            for col_name, data in self.collections.items():
                col_dir = VIRTUAL_DRIVE_DIR / col_name
                col_dir.mkdir(parents=True, exist_ok=True)

                for filepath in data.get("filepaths", []):
                    target = Path(filepath)
                    if target.exists():
                        shortcut = col_dir / f"{target.name}.url"
                        if not shortcut.exists():
                            with open(shortcut, "w", encoding="utf-8") as f:
                                target_url = str(target.absolute()).replace("\\", "/")
                                f.write(f"[InternetShortcut]\nURL=file:///{target_url}\n")
        except Exception as e:
            logger.debug(f"sync_virtual_drive error: {e}")
