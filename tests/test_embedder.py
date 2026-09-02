from __future__ import annotations

from semanticfs.embedder import Embedder

def test_embed_text():
    embedder = Embedder()
    vector = embedder.embed_text("hello world")
    assert isinstance(vector, list)
    assert len(vector) == 384  # MiniLM dimension
    assert isinstance(vector[0], float)

def test_embed_batch():
    embedder = Embedder()
    vectors = embedder.embed_batch(["hello", "world"])
    assert isinstance(vectors, list)
    assert len(vectors) == 2
    assert len(vectors[0]) == 384


def test_extract_content_xlsx_early_breakout(tmp_path):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "DataSheet"
    for i in range(150):
        ws.append([f"RowVal_{i}", f"Data_{i}"])
    xlsx_file = tmp_path / "large_sheet.xlsx"
    wb.save(xlsx_file)
    wb.close()

    embedder = Embedder()
    extracted = embedder._extract_content(xlsx_file)
    lines = [line for line in extracted.splitlines() if line.strip()]

    # 1 sheet header + exactly 100 data rows = 101 non-empty lines total
    assert len(lines) == 101
    assert "RowVal_0" in extracted
    assert "RowVal_99" in extracted
    assert "RowVal_100" not in extracted
