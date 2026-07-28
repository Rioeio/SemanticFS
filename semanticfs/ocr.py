from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    shutil.which("tesseract") or ""
]

def get_tesseract_cmd() -> str | None:
    for path in TESSERACT_PATHS:
        if path and os.path.exists(path):
            return path
    return None

def extract_ocr_text(filepath: Path) -> str:
    """Extract printed text from images, receipts, screenshots, and scanned docs via OCR."""
    if not filepath.exists():
        return ""
        
    ext = filepath.suffix.lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.pdf'):
        return ""

    tess_cmd = get_tesseract_cmd()
    
    # Method 1: PyTesseract / Tesseract CLI
    if tess_cmd:
        try:
            import pytesseract
            from PIL import Image
            pytesseract.pytesseract.tesseract_cmd = tess_cmd
            with Image.open(filepath) as img:
                text = pytesseract.image_to_string(img)
                if text and len(text.strip()) > 3:
                    logger.debug(f"PyTesseract extracted {len(text)} chars from {filepath.name}")
                    return text.strip()
        except Exception:
            pass

        try:
            # Direct Tesseract CLI subprocess invocation
            res = subprocess.run([tess_cmd, str(filepath.absolute()), "stdout"], capture_output=True, text=True, timeout=8.0)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass

    # Method 2: EasyOCR fallback
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(str(filepath.absolute()), detail=0)
        if results:
            return " ".join(results).strip()
    except Exception:
        pass

    return ""
