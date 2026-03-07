from __future__ import annotations

import os
from pathlib import Path


def save_bytes_to_uploads(filename: str, content: bytes, uploads_dir: str = "uploads") -> str:
    safe_name = Path(filename).name
    os.makedirs(uploads_dir, exist_ok=True)

    rel_path = str(Path(uploads_dir) / safe_name)
    with open(rel_path, "wb") as f:
        f.write(content)

    return rel_path

