"""
Audio duration validation.
"""

from ..config import (
    MIN_DURATION,
    RECOMMENDED_MIN_DURATION,
    MAX_DURATION,
)
from ..utils.audio import AudioInfo


def check_duration(audio_info: AudioInfo) -> tuple[bool, str]:
    """
    Check whether the audio duration is valid.

    Returns
    -------
    tuple
        (status, message)
    """

    duration = audio_info.duration

    if duration < MIN_DURATION:
        return (
            False,
            f"Too short ({duration:.2f}s). Minimum: {MIN_DURATION:.2f}s."
        )

    if duration < RECOMMENDED_MIN_DURATION:
        return (
            True,
            f"Acceptable ({duration:.2f}s), but below the recommended "
            f"{RECOMMENDED_MIN_DURATION:.2f}s."
        )

    if duration > MAX_DURATION:
        return (
            False,
            f"Too long ({duration:.2f}s). Maximum: {MAX_DURATION:.2f}s."
        )

    return (
        True,
        f"{duration:.2f}s."
    )