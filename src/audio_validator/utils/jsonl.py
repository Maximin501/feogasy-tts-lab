"""
JSONL utilities.
"""

from pathlib import Path
import json


def load_jsonl(file_path: Path) -> list[dict]:
    """
    Load a JSONL file.

    Parameters
    ----------
    file_path : Path

    Returns
    -------
    list[dict]
    """

    records = []

    with file_path.open("r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    return records