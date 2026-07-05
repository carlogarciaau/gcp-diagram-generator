"""Loading of Cloud Asset Inventory JSONL snapshot files."""

import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    """Read a newline-delimited JSON asset snapshot file.

    Returns an empty list if the file does not exist, since not every
    content type is required to generate a diagram.
    """
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]
