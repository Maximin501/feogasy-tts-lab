"""
Transcript validation.
"""

from pathlib import Path

from ..utils.jsonl import load_jsonl


def check_transcripts(
    manifest_path: Path,
    dataset_root: Path,
) -> list[dict]:
    """
    Validate transcripts and referenced audio files.

    Returns
    -------
    list[dict]
    """

    records = load_jsonl(manifest_path)

    results = []

    for record in records:

        audio = record.get("audio")
        text = record.get("text")

        audio_path = dataset_root / audio

        # Audio exists
        if not audio_path.exists():

            results.append(
                {
                    "audio": audio,
                    "status": False,
                    "message": "Audio file not found.",
                }
            )

            continue

        # Transcript exists
        if text is None or text.strip() == "":

            results.append(
                {
                    "audio": audio,
                    "status": False,
                    "message": "Missing transcript.",
                }
            )

            continue

        results.append(
            {
                "audio": audio,
                "status": True,
                "message": "Transcript OK.",
            }
        )

    return results