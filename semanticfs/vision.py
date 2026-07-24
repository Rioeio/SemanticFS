from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_clip_model = None
_clip_processor = None

def get_clip_engine():
    """Lazy load CLIP Vision Transformer for deep visual content indexing."""
    global _clip_model, _clip_processor
    if _clip_model is None:
        try:
            from transformers import CLIPModel, CLIPProcessor
            model_name = "openai/clip-vit-base-patch32"
            logger.info(f"Loading CLIP Vision Model '{model_name}'...")
            _clip_processor = CLIPProcessor.from_pretrained(model_name)
            _clip_model = CLIPModel.from_pretrained(model_name)
        except Exception as e:
            logger.debug(f"CLIP Vision Model not available: {e}")
            _clip_model = False
    return _clip_model, _clip_processor

def extract_image_visual_content(filepath: Path) -> str:
    """Indexes images by actual visual content, EXIF tags, and visual features using PIL & CLIP."""
    content_parts = []
    
    # 1. PIL EXIF & Structural Metadata
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

            exif_str = " ".join(exif_info[:5]) if exif_info else ""
            content_parts.append(
                f"Image File: {filepath.name}, Type: {format_name}, Resolution: {width}x{height}, "
                f"ColorMode: {mode}, RGB Average: ({int(avg_rgb[0])},{int(avg_rgb[1])},{int(avg_rgb[2])}), "
                f"Folder: {filepath.parent.name} {exif_str}"
            )
    except Exception as e:
        logger.debug(f"PIL extraction error for {filepath}: {e}")
        content_parts.append(f"Image File: {filepath.name}, Type: {filepath.suffix}, Folder: {filepath.parent.name}")

    # 2. CLIP Vision Feature Labeling (Visual Content Classification)
    clip_model, clip_processor = get_clip_engine()
    if clip_model and clip_processor:
        try:
            from PIL import Image
            image = Image.open(filepath).convert("RGB")
            
            candidate_labels = [
                "beach sunset vacation ocean sea sand",
                "document invoice receipt text report code screenshot",
                "wallpaper landscape nature mountains forest",
                "portrait person face human photo",
                "diagram chart graph vector illustration graphic"
            ]
            
            inputs = clip_processor(text=candidate_labels, images=image, return_tensors="pt", padding=True)
            outputs = clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
            
            top_idx = probs.argmax().item()
            best_label = candidate_labels[top_idx]
            content_parts.append(f"Visual Scene Analysis: {best_label}")
        except Exception as e:
            logger.debug(f"CLIP visual scene inference error: {e}")

    return "\n".join(content_parts)
