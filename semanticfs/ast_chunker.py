from __future__ import annotations

import ast
import logging
from pathlib import Path

from semanticfs.chunker import FileChunk

logger = logging.getLogger(__name__)

def chunk_python_ast(filepath: Path, content: str) -> list[FileChunk]:
    """Chunk Python files cleanly at AST function (def) and class (class) boundaries."""
    chunks: list[FileChunk] = []
    lines = content.splitlines()
    if not lines:
        return chunks

    try:
        tree = ast.parse(content)
        chunk_idx = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start_l = getattr(node, "lineno", 1)
                end_l = getattr(node, "end_lineno", min(start_l + 30, len(lines)))

                block_code = "\n".join(lines[start_l - 1:end_l])
                if len(block_code.strip()) > 15:
                    chunks.append(FileChunk(
                        chunk_id=f"{filepath}#chunk_{chunk_idx}",
                        parent_filepath=str(filepath),
                        filename=filepath.name,
                        text=block_code,
                        start_line=start_l,
                        end_line=end_l,
                        chunk_index=chunk_idx
                    ))
                    chunk_idx += 1

        # Fallback if no functions/classes found
        if not chunks:
            chunks.append(FileChunk(
                chunk_id=f"{filepath}#chunk_0",
                parent_filepath=str(filepath),
                filename=filepath.name,
                text=content[:5000],
                start_line=1,
                end_line=len(lines),
                chunk_index=0
            ))

        return chunks[:25]
    except Exception as e:
        logger.debug(f"AST parsing fallback for {filepath.name}: {e}")
        return []

def chunk_markdown_headers(filepath: Path, content: str) -> list[FileChunk]:
    """Chunk Markdown files cleanly at header (# / ## / ###) boundaries."""
    chunks: list[FileChunk] = []
    lines = content.splitlines()
    if not lines:
        return chunks

    current_block: list[str] = []
    start_line = 1
    chunk_idx = 0

    for i, line in enumerate(lines, start=1):
        if line.startswith(('# ', '## ', '### ')) and current_block:
            text = "\n".join(current_block)
            if len(text.strip()) > 15:
                chunks.append(FileChunk(
                    chunk_id=f"{filepath}#chunk_{chunk_idx}",
                    parent_filepath=str(filepath),
                    filename=filepath.name,
                    text=text,
                    start_line=start_line,
                    end_line=i - 1,
                    chunk_index=chunk_idx
                ))
                chunk_idx += 1
            current_block = [line]
            start_line = i
        else:
            current_block.append(line)

    if current_block:
        text = "\n".join(current_block)
        if len(text.strip()) > 15:
            chunks.append(FileChunk(
                chunk_id=f"{filepath}#chunk_{chunk_idx}",
                parent_filepath=str(filepath),
                filename=filepath.name,
                text=text,
                start_line=start_line,
                end_line=len(lines),
                chunk_index=chunk_idx
            ))

    return chunks[:25]
