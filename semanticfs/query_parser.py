from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StructuredQuery:
    raw_query: str
    semantic_text: str
    extensions: list[str] = field(default_factory=list)
    filename_contains: list[str] = field(default_factory=list)
    folder_contains: list[str] = field(default_factory=list)
    tag_query: str | None = None
    must_include: list[str] = field(default_factory=list)
    must_exclude: list[str] = field(default_factory=list)
    min_score: float | None = None

def parse_structured_query(query_str: str) -> StructuredQuery:
    """Parses structured query operators (ext:, file:, in:, tag:, +word, -word) into sharp filters."""
    extensions = []
    filename_contains = []
    folder_contains = []
    must_include = []
    must_exclude = []
    tag_query = None
    min_score = None

    clean_parts = []
    tokens = query_str.split()

    for token in tokens:
        lower_token = token.lower()
        if lower_token.startswith("ext:") or lower_token.startswith("type:"):
            val = token.split(":", 1)[1].strip().lower()
            val = val if val.startswith(".") else f".{val}"
            extensions.append(val)
        elif lower_token.startswith("file:") or lower_token.startswith("name:"):
            val = token.split(":", 1)[1].strip().lower()
            filename_contains.append(val)
        elif lower_token.startswith("in:") or lower_token.startswith("path:") or lower_token.startswith("dir:"):
            val = token.split(":", 1)[1].strip().lower()
            folder_contains.append(val)
        elif lower_token.startswith("tag:") or lower_token.startswith("note:"):
            tag_query = token.split(":", 1)[1].strip().lower()
        elif lower_token.startswith("score:"):
            try:
                min_score = float(token.split(":", 1)[1])
            except Exception:
                pass
        elif token.startswith("+") and len(token) > 1:
            must_include.append(token[1:].lower())
        elif token.startswith("-") and len(token) > 1:
            must_exclude.append(token[1:].lower())
        else:
            clean_parts.append(token)

    semantic_text = " ".join(clean_parts).strip()
    if not semantic_text:
        semantic_text = query_str  # Fallback

    return StructuredQuery(
        raw_query=query_str,
        semantic_text=semantic_text,
        extensions=extensions,
        filename_contains=filename_contains,
        folder_contains=folder_contains,
        tag_query=tag_query,
        must_include=must_include,
        must_exclude=must_exclude,
        min_score=min_score
    )
