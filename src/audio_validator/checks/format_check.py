"""
Audio format validation.
"""

from pathlib import Path

from ..config import RECOMMENDED_FORMAT, SUPPORTED_AUDIO_FORMATS


def check_audio_format(audio_path: Path) -> tuple[bool, str]:
    """
    Check if the audio file format is supported.
    """

    extension = audio_path.suffix.lower()

    if extension not in SUPPORTED_AUDIO_FORMATS:
        return (
            False,
            f"Unsupported format '{extension}'. "
            f"Supported: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
        )

    if extension != RECOMMENDED_FORMAT:
        return (
            True,
            f"Supported but not recommended ({extension})."
        )

    return True, "Recommended format."