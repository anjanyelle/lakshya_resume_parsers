import os
from pathlib import Path
from uuid import uuid4


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def generate_storage_path(storage_dir: str, original_filename: str) -> str:
    ensure_dir(storage_dir)
    _, ext = os.path.splitext(original_filename)
    filename = f"{uuid4()}{ext}"
    return str(Path(storage_dir) / filename)
