"""
Sample rate validation.
"""

from ..config import TARGET_SAMPLE_RATE
from ..utils.audio import AudioInfo


def check_sample_rate(audio_info: AudioInfo) -> tuple[bool, str]:
    """
    Check whether the sample rate matches the recommended value.
    """

    if audio_info.sample_rate != TARGET_SAMPLE_RATE:
        return (
            False,
            f"Expected {TARGET_SAMPLE_RATE} Hz, got {audio_info.sample_rate} Hz."
        )

    return True, f"{audio_info.sample_rate} Hz."