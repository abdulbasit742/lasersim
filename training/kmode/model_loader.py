"""Model loading helpers for trained K-mode models."""

from pathlib import Path


def find_checkpoint(folder="training/checkpoints"):
    path = Path(folder)
    if not path.exists():
        return None
    files = list(path.glob("*.pt"))
    return str(sorted(files)[-1]) if files else None
