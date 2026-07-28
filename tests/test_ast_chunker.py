from __future__ import annotations

from pathlib import Path
from semanticfs.ast_chunker import chunk_python_ast, chunk_markdown_headers

def test_chunk_python_ast():
    code = '''
def calculate_area(radius: float) -> float:
    """Calculate area of a circle."""
    import math
    return math.pi * radius ** 2

class GeometryEngine:
    def __init__(self):
        self.scale = 1.0

    def compute_volume(self, length: float, width: float, height: float) -> float:
        return length * width * height * self.scale
'''
    dummy_path = Path("sample.py")
    chunks = chunk_python_ast(dummy_path, code)
    assert len(chunks) >= 2
    texts = [c.text for c in chunks]
    assert any("calculate_area" in t for t in texts)
    assert any("GeometryEngine" in t for t in texts)

def test_chunk_markdown_headers():
    md = '''# Main Header

This is introduction text.

## Section 1: Features
- Feature A
- Feature B

## Section 2: Architecture
Architecture details here.
'''
    dummy_path = Path("sample.md")
    chunks = chunk_markdown_headers(dummy_path, md)
    assert len(chunks) >= 2
    texts = [c.text for c in chunks]
    assert any("Section 1: Features" in t for t in texts)
    assert any("Section 2: Architecture" in t for t in texts)
