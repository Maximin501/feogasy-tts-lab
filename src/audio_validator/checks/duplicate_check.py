from pathlib import Path

from ..utils.hashing import compute_sha256


def check_duplicates(audio_files: list[Path]) -> dict[Path, tuple[bool, str]]:
    """
    Detect duplicate audio files using SHA-256.
    """

    hashes: dict[str, Path] = {}
    results: dict[Path, tuple[bool, str]] = {}

    # On traite d'abord les fichiers "valid", puis les autres
    ordered_files = sorted(
        audio_files,
        key=lambda p: (
            "valid" not in p.parts,
            str(p),
        ),
    )

    for audio in ordered_files:

        file_hash = compute_sha256(audio)

        if file_hash in hashes:

            original = hashes[file_hash]

            results[audio] = (
                False,
                f"Duplicate of '{original.name}'.",
            )

        else:

            hashes[file_hash] = audio

            results[audio] = (
                True,
                "Unique file.",
            )

    return results