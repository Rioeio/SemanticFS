from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def extract_image_visual_metadata(filepath: Path) -> str:
    """Extracts visual metadata, EXIF tags, dimensions, and image color metrics for multimodal search."""
    try:
        from PIL import Image, ImageStat
        with Image.open(filepath) as img:
            width, height = img.size
            format_name = img.format
            mode = img.mode

            stat = ImageStat.Stat(img)
            avg_rgb = stat.mean[:3] if len(stat.mean) >= 3 else [128, 128, 128]
            
            exif_info = []
            if hasattr(img, "_getexif") and img._getexif():
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, val in exif_data.items():
                        if isinstance(val, str) and len(val) < 50:
                            exif_info.append(val)

            exif_str = " ".join(exif_info[:5]) if exif_info else "No EXIF"
            
            return (
                f"Image File: {filepath.name}, Type: {format_name}, Resolution: {width}x{height}, "
                f"ColorMode: {mode}, RGB: ({int(avg_rgb[0])},{int(avg_rgb[1])},{int(avg_rgb[2])}), "
                f"Folder: {filepath.parent.name}, EXIF: {exif_str}"
            )
    except Exception as e:
        logger.debug(f"PIL vision extraction fallback for {filepath}: {e}")
        return f"Image File: {filepath.name}, Type: {filepath.suffix}, Folder: {filepath.parent.name}"
