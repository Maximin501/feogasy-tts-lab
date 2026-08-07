"""
Audio peak level validation.
"""

from ..config import MAX_PEAK, WARNING_PEAK
from ..utils.audio import AudioInfo


def check_peak(audio_info: AudioInfo) -> tuple[bool, str]:
    """
    Check the audio peak level and detect clipping.

    Returns
    -------
    tuple
        (status, message)
    """

    peak = audio_info.peak

    if peak >= MAX_PEAK:
        return (
            False,
            f"Clipping detected (peak={peak:.3f})."
        )

    if peak >= WARNING_PEAK:
        return (
            True,
            f"Peak very close to clipping ({peak:.3f})."
        )

    return (
        True,
        f"Peak OK ({peak:.3f})."
    )