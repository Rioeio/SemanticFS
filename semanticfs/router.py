from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Set

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg", ".raw", ".heic"}
AUDIO_EXTS = {".mp3", ".m4p", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"}
VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv"}
DOC_EXTS = {".pdf", ".docx", ".doc", ".txt", ".md", ".tex"}
SLIDE_EXTS = {".pptx", ".ppt", ".key"}
SHEET_EXTS = {".xlsx", ".xls", ".csv", ".tsv"}
CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".c", ".cpp", ".h", ".java", ".rs", ".go", ".cs", ".sql", ".sh", ".bat", ".ps1"}

IMAGE_KEYWORDS = {"picture", "pictures", "photo", "photos", "image", "images", "pic", "pics", "wallpaper", "snapshot", "snapshots"}
AUDIO_KEYWORDS = {"song", "songs", "music", "track", "tracks", "audio", "mp3", "playlist", "playlists", "album", "artist"}
VIDEO_KEYWORDS = {"video", "videos", "movie", "movies", "clip", "clips", "film", "recording"}
SLIDE_KEYWORDS = {"presentation", "presentations", "slide", "slides", "powerpoint", "deck", "ppt", "pptx"}
SHEET_KEYWORDS = {"spreadsheet", "spreadsheets", "excel", "sheet", "sheets", "csv", "xlsx"}
CODE_KEYWORDS = {"code", "script", "scripts", "function", "functions", "class", "program"}

@dataclass
class QueryIntent:
    clean_query: str
    target_exts: Set[str]
    intent_category: str | None

def detect_query_intent(query: str) -> QueryIntent:
    words = re.findall(r'\b\w+\b', query.lower())
    target_exts: Set[str] = set()
    category: str | None = None

    for w in words:
        if w in IMAGE_KEYWORDS:
            target_exts.update(IMAGE_EXTS)
            category = "image"
        elif w in AUDIO_KEYWORDS:
            target_exts.update(AUDIO_EXTS)
            category = "audio"
        elif w in VIDEO_KEYWORDS:
            target_exts.update(VIDEO_EXTS)
            category = "video"
        elif w in SLIDE_KEYWORDS:
            target_exts.update(SLIDE_EXTS)
            category = "slide"
        elif w in SHEET_KEYWORDS:
            target_exts.update(SHEET_EXTS)
            category = "sheet"
        elif w in CODE_KEYWORDS:
            target_exts.update(CODE_EXTS)
            category = "code"

    return QueryIntent(
        clean_query=query,
        target_exts=target_exts,
        intent_category=category
    )
