from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from rich.console import Console

from semanticfs.config import Config
from semanticfs.store import VectorStore

console = Console()
logger = logging.getLogger(__name__)

def train_local_model(epochs: int = 1, output_dir: Path | None = None) -> Path:
    """Fine-tunes the local sentence-transformer model on the user's indexed codebase/files."""
    from sentence_transformers import InputExample, SentenceTransformer, losses
    from torch.utils.data import DataLoader

    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)

    if output_dir is None:
        output_dir = Path("~/.semanticfs/custom_model").expanduser()

    items = store.get_all(limit=2000)
    if not items:
        console.print("[yellow]No files found in vector index to train on. Run 'sfind reindex' first.[/yellow]")
        return output_dir

    console.print(f"[bold cyan]🧠 Preparing local training dataset from {len(items)} indexed files...[/bold cyan]")

    train_examples: list[InputExample] = []
    for item in items:
        filename = item.get("filename", "")
        filepath = item.get("filepath", "")
        snippet = item.get("content_snippet", "")
        context = item.get("context_window", "")

        if not filename:
            continue

        # Pair 1: Filename <-> Snippet / Content
        if snippet:
            train_examples.append(InputExample(texts=[filename, snippet[:300]]))

        # Pair 2: Filepath <-> Filename + Context
        if context:
            train_examples.append(InputExample(texts=[f"{filename} in {filepath}", context]))

    if not train_examples:
        console.print("[yellow]Not enough text content extracted to train local model.[/yellow]")
        return output_dir

    console.print(f"[bold green]✔ Generated {len(train_examples)} local training pairs.[/bold green]")
    console.print(f"[bold cyan]⚡ Fine-tuning '{config.embedding.model_name}' on local dataset...[/bold cyan]")

    model = SentenceTransformer(config.embedding.model_name)
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
    train_loss = losses.MultipleNegativesRankingLoss(model)

    output_dir.mkdir(parents=True, exist_ok=True)

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=epochs,
        warmup_steps=10,
        show_progress_bar=True
    )

    model.save(str(output_dir))
    console.print(f"[bold green]🎉 Local AI model successfully trained & saved to:[/bold green] {output_dir}")
    return output_dir
