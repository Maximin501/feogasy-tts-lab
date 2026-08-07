"""
Audio channels validation.
"""

from ..config import RECOMMENDED_CHANNELS
from ..utils.audio import AudioInfo


def check_channels(audio_info: AudioInfo) -> tuple[bool, str]:
    """
    Check whether the audio has the recommended number of channels.
    """

    if audio_info.channels != RECOMMENDED_CHANNELS:
        return (
            False,
            f"Expected {RECOMMENDED_CHANNELS} channel(s), got {audio_info.channels}."
        )

    return True, f"{audio_info.channels} channel(s)."