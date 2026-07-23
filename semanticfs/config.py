from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class EmbeddingConfig:
    model_name: str = "all-MiniLM-L6-v2"
    max_tokens: int = 512

@dataclass
class StorageConfig:
    db_path: Path = Path("~/.semanticfs/chroma").expanduser()
    links_db_path: Path = Path("~/.semanticfs/links.db").expanduser()
    collection_name: str = "file_embeddings"

@dataclass
class ContextConfig:
    enabled: bool = True

@dataclass
class WatcherConfig:
    watch_directories: list[Path] = field(default_factory=list)
    include_patterns: list[str] = field(default_factory=lambda: ["*"])
    exclude_patterns: list[str] = field(default_factory=lambda: [".git*", "*.tmp"])
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    debounce_ms: int = 500

@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 7777

@dataclass
class LinkerConfig:
    db_path: Path = Path("~/.semanticfs/linker.db").expanduser()
    co_access_window_seconds: int = 300
    min_link_weight: float = 1.0

@dataclass
class Config:
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    context: ContextConfig = field(default_factory=ContextConfig)
    watcher: WatcherConfig = field(default_factory=WatcherConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    linker: LinkerConfig = field(default_factory=LinkerConfig)

    _instance: Config | None = None
    _config_path: Path = Path("C:/Dev/SemanticFS/config/default.yaml")

    @classmethod
    def get_instance(cls, config_path: Path | None = None) -> Config:
        if cls._instance is None:
            cls._instance = cls._load(config_path)
        return cls._instance

    @classmethod
    def _load(cls, config_path: Path | None = None) -> Config:
        default_path = Path("C:/Dev/SemanticFS/config/default.yaml")
        path_to_load = config_path if config_path else default_path
        
        data: dict[str, Any] = {}
        if path_to_load.exists():
            with open(path_to_load, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    data = loaded

        def get_env_or_dict(section, key, default, type_func=str):
            env_key = f"SEMANTICFS_{section.upper()}_{key.upper()}"
            if env_key in os.environ:
                return type_func(os.environ[env_key])
            if section in data and key in data[section]:
                return type_func(data[section][key])
            return default

        watch_dirs_raw = data.get("watcher", {}).get("watch_directories", [])
        if "watch_directories" in data:
            watch_dirs_raw = data["watch_directories"]
            
        watch_dirs = [Path(d) for d in watch_dirs_raw] if watch_dirs_raw else []
        
        inc_patterns = data.get("watcher", {}).get("include_patterns") or data.get("include_patterns") or ["*"]
        exc_patterns = data.get("watcher", {}).get("exclude_patterns") or data.get("exclude_patterns") or [".git*", "*.tmp"]

        cfg = cls(
            embedding=EmbeddingConfig(
                model_name=get_env_or_dict("embedding", "model_name", "all-MiniLM-L6-v2"),
                max_tokens=get_env_or_dict("embedding", "max_tokens", 512, int),
            ),
            storage=StorageConfig(
                db_path=Path(get_env_or_dict("storage", "db_path", "~/.semanticfs/chroma")).expanduser(),
                links_db_path=Path(get_env_or_dict("storage", "links_db_path", "~/.semanticfs/links.db")).expanduser(),
                collection_name=get_env_or_dict("storage", "collection_name", "file_embeddings"),
            ),
            context=ContextConfig(
                enabled=get_env_or_dict("context", "enabled", True, lambda x: str(x).lower() == "true"),
            ),
            watcher=WatcherConfig(
                watch_directories=watch_dirs,
                include_patterns=inc_patterns,
                exclude_patterns=exc_patterns,
                max_file_size=get_env_or_dict("watcher", "max_file_size", 10 * 1024 * 1024, int),
                debounce_ms=get_env_or_dict("watcher", "debounce_ms", 500, int),
            ),
            server=ServerConfig(
                host=get_env_or_dict("server", "host", "127.0.0.1"),
                port=get_env_or_dict("server", "port", 7777, int),
            ),
            linker=LinkerConfig(
                db_path=Path(get_env_or_dict("linker", "db_path", "~/.semanticfs/linker.db")).expanduser(),
                co_access_window_seconds=get_env_or_dict("linker", "co_access_window_seconds", 300, int),
                min_link_weight=get_env_or_dict("linker", "min_link_weight", 1.0, float),
            )
        )
        cfg._config_path = path_to_load
        return cfg

    def save(self) -> None:
        """Persist current configuration to YAML file."""
        data = {
            "watch_directories": [str(p) for p in self.watcher.watch_directories],
            "include_patterns": self.watcher.include_patterns,
            "exclude_patterns": self.watcher.exclude_patterns,
            "embedding": {
                "model_name": self.embedding.model_name,
                "max_tokens": self.embedding.max_tokens,
            },
            "storage": {
                "db_path": str(self.storage.db_path),
                "links_db_path": str(self.storage.links_db_path),
                "collection_name": self.storage.collection_name,
            },
            "context": {
                "enabled": self.context.enabled,
            },
            "watcher": {
                "debounce_ms": self.watcher.debounce_ms,
                "max_file_size": self.watcher.max_file_size,
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
            },
            "linker": {
                "co_access_window_seconds": self.linker.co_access_window_seconds,
                "min_link_weight": self.linker.min_link_weight,
            }
        }
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)
