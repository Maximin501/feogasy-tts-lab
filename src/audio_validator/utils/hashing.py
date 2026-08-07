"""
Hash utilities.
"""

from pathlib import Path
import hashlib


def compute_sha256(file_path: Path, chunk_size: int = 8192) -> str:
    """
    Compute the SHA-256 hash of a file.

    Parameters
    ----------
    file_path : Path
        Path to the file.
    chunk_size : int
        Number of bytes read at each iteration.

    Returns
    -------
    str
        SHA-256 hash.
    """

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(chunk_size):
            sha256.update(chunk)

    return sha256.hexdigest()