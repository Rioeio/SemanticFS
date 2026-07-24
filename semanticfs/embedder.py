from __future__ import annotations

import functools
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class Embedder:
    """Embeds text and files into vectors, with support for local fine-tuned models and all file types."""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", max_tokens: int = 512):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self._model: Any = None

        # Check for custom fine-tuned model
        custom_model_dir = Path("~/.semanticfs/custom_model").expanduser()
        if custom_model_dir.exists():
            self.model_path = str(custom_model_dir)
        else:
            self.model_path = model_name

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Loading embedding model from '{self.model_path}'...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_path)
        return self._model

    @functools.lru_cache(maxsize=256)
    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string with LRU caching."""
        truncated = text[:self.max_tokens * 4] 
        embedding = self.model.encode(truncated)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embed multiple texts."""
        truncated_texts = [text[:self.max_tokens * 4] for text in texts]
        embeddings = self.model.encode(truncated_texts)
        return embeddings.tolist()

    def embed_file(self, filepath: Path) -> list[float]:
        """Read file content, combine with filename and path metadata, generate embedding."""
        content = self._extract_content(filepath)
        text = f"Filename: {filepath.name}\nPath: {filepath.absolute()}\nContent:\n{content}"
        return self.embed_text(text)

    def _extract_content(self, filepath: Path) -> str:
        """Extract text from text, code, document, tabular, or binary files gracefully."""
        ext = filepath.suffix.lower()
        content = ""
        try:
            if ext == ".pdf":
                import fitz  # PyMuPDF
                doc = fitz.open(filepath)
                for page in doc:
                    content += page.get_text()
                doc.close()
            elif ext == ".docx":
                import docx
                doc = docx.Document(filepath)
                content = "\n".join([p.text for p in doc.paragraphs])
            elif ext in (".xlsx", ".xls", ".csv", ".tsv"):
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(3000)
            elif ext in (".ipynb", ".json", ".yaml", ".yml", ".toml", ".xml"):
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(3000)
            elif ext in (".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".c", ".cpp", ".h", ".hpp", ".cs", ".java", ".rs", ".go", ".rb", ".php", ".swift", ".kt", ".md", ".txt", ".sh", ".bat", ".ps1", ".sql", ".r", ".R", ".log"):
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(3000)
            else:
                # Binary files (images, audio, video, zip, etc.) — index rich file metadata
                stat = filepath.stat() if filepath.exists() else None
                size_kb = round(stat.st_size / 1024, 1) if stat else 0
                content = f"Media/Binary File: {filepath.name}, Type: {ext}, Folder: {filepath.parent.name}, Size: {size_kb} KB"
        except Exception as e:
            logger.debug(f"Error extracting content from {filepath}: {e}")
            content = f"File: {filepath.name}, Type: {ext}, Folder: {filepath.parent.name}"
        return content
