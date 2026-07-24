from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    overlap_words: int = 40
) -> list[FileChunk]:
    """Dynamically splits long files into overlapping semantic chunks with line number tracking."""
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

    lines = content.splitlines()
    total_lines = len(lines)

    # If file is small (< 250 words or < 50 lines), return 1 single chunk
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
        line_words = len(line.split())
        current_lines.append(line)
        current_word_count += line_words

        if current_word_count >= max_words or line_idx == total_lines:
            chunk_text = "\n".join(current_lines)
            end_line = line_idx
            
            header = f"Filename: {filepath.name}\nPath: {filepath.absolute()}\nLines {start_line}-{end_line}\n\n"
            full_chunk_text = header + chunk_text

            chunks.append(
                FileChunk(
                    chunk_id=f"{filepath.absolute()}#chunk_{chunk_idx}",
                    parent_filepath=str(filepath.absolute()),
                    filename=filepath.name,
                    text=full_chunk_text,
                    start_line=start_line,
                    end_line=end_line,
                    chunk_index=chunk_idx
                )
            )

            # Slide window: keep last few lines for overlap
            overlap_count = 0
            overlap_lines: list[str] = []
            for prev_line in reversed(current_lines):
                w_cnt = len(prev_line.split())
                if overlap_count + w_cnt <= overlap_words:
                    overlap_lines.insert(0, prev_line)
                    overlap_count += w_cnt
                else:
                    break

            current_lines = overlap_lines
            current_word_count = overlap_count
            start_line = max(1, end_line - len(overlap_lines) + 1)
            chunk_idx += 1

    return chunks
