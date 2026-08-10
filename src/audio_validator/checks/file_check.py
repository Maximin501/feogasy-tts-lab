"""
File validation checks.
"""

from pathlib import Path

from ..utils.audio import read_audio_info


def check_file_exists(audio_path: Path) -> tuple[bool, str]:
    """
    Check whether the audio file exists.

    Returns
    -------
    tuple
        (status, message)
    """
    if not audio_path.exists():
        return False, "File not found."

    return True, "File exists."


def check_file_readable(audio_path: Path) -> tuple[bool, str]:
    """
    Check whether the audio file can be read.
    """
    try:
        read_audio_info(audio_path)
        return True, "Audio readable."

    except Exception as exc:
        return False, str(exc)