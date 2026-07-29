from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileChunk:
    chunk_id: str
    parent_filepath: str
    filename: str
    text: str
    start_line: int
    end_line: int
    chunk_index: int

def chunk_file_content(
    filepath: Path,
    content: str,
    max_words: int = 200,
    overlap_words: int = 40,
    max_chunks_per_file: int = 25
) -> list[FileChunk]:
    """Dynamically splits long files into overlapping semantic chunks with line number tracking and AST/Header awareness."""
    if not content or not content.strip():
        return [
            FileChunk(
                chunk_id=f"{filepath.absolute()}#chunk_0",
                parent_filepath=str(filepath.absolute()),
                filename=filepath.name,
                text=f"Filename: {filepath.name}\nPath: {filepath.absolute()}",
                start_line=1,
                end_line=1,
                chunk_index=0
            )
        ]

    ext = filepath.suffix.lower()

    # 1. AST Python Function & Class Syntax Chunker
    if ext == ".py":
        try:
            from semanticfs.ast_chunker import chunk_python_ast
            ast_chunks = chunk_python_ast(filepath, content)
            if ast_chunks:
                return [
                    FileChunk(
                        chunk_id=f"{filepath.absolute()}#chunk_{c.chunk_index}",
                        parent_filepath=str(filepath.absolute()),
                        filename=filepath.name,
                        text=f"File: {filepath.name}\nLines {c.start_line}-{c.end_line}\n\n{c.text}",
                        start_line=c.start_line,
                        end_line=c.end_line,
                        chunk_index=c.chunk_index
                    )
                    for c in ast_chunks
                ]
        except Exception:
            pass

    # 2. Markdown Header Chunker
    if ext == ".md":
        try:
            from semanticfs.ast_chunker import chunk_markdown_headers
            md_chunks = chunk_markdown_headers(filepath, content)
            if md_chunks:
                return [
                    FileChunk(
                        chunk_id=f"{filepath.absolute()}#chunk_{c.chunk_index}",
                        parent_filepath=str(filepath.absolute()),
                        filename=filepath.name,
                        text=f"File: {filepath.name}\nLines {c.start_line}-{c.end_line}\n\n{c.text}",
                        start_line=c.start_line,
                        end_line=c.end_line,
                        chunk_index=c.chunk_index
                    )
                    for c in md_chunks
                ]
        except Exception:
            pass

    lines = content.splitlines()
    total_lines = len(lines)

    words = content.split()
    if len(words) <= max_words or total_lines <= 40:
        return [
            FileChunk(
                chunk_id=f"{filepath.absolute()}#chunk_0",
                parent_filepath=str(filepath.absolute()),
                filename=filepath.name,
                text=f"Filename: {filepath.name}\nPath: {filepath.absolute()}\nLines 1-{total_lines}\n\nContent:\n{content[:2000]}",
                start_line=1,
                end_line=total_lines,
                chunk_index=0
            )
        ]

    chunks: list[FileChunk] = []
    chunk_idx = 0
    current_lines: list[str] = []
    current_word_count = 0
    start_line = 1

    for line_idx, line in enumerate(lines, start=1):
        line_words = line.split()
        current_lines.append(line)
        current_word_count += len(line_words)

        if current_word_count >= max_words:
            end_line = line_idx
            chunk_text = f"Filename: {filepath.name}\nPath: {filepath.absolute()}\nLines {start_line}-{end_line}\n\nContent:\n" + "\n".join(current_lines)

            chunks.append(
                FileChunk(
                    chunk_id=f"{filepath.absolute()}#chunk_{chunk_idx}",
                    parent_filepath=str(filepath.absolute()),
                    filename=filepath.name,
                    text=chunk_text,
                    start_line=start_line,
                    end_line=end_line,
                    chunk_index=chunk_idx
                )
            )

            chunk_idx += 1
            if chunk_idx >= max_chunks_per_file:
                break

            overlap_line_count = min(len(current_lines), max(1, int(len(current_lines) * 0.2)))
            current_lines = current_lines[-overlap_line_count:]
            current_word_count = sum(len(line_str.split()) for line_str in current_lines)
            start_line = max(1, line_idx - overlap_line_count + 1)

    if current_lines and chunk_idx < max_chunks_per_file:
        end_line = total_lines
        chunk_text = f"Filename: {filepath.name}\nPath: {filepath.absolute()}\nLines {start_line}-{end_line}\n\nContent:\n" + "\n".join(current_lines)
        chunks.append(
            FileChunk(
                chunk_id=f"{filepath.absolute()}#chunk_{chunk_idx}",
                parent_filepath=str(filepath.absolute()),
                filename=filepath.name,
                text=chunk_text,
                start_line=start_line,
                end_line=end_line,
                chunk_index=chunk_idx
            )
        )

    return chunks
