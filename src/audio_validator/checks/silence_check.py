"""
Trailing silence validation.
"""

import numpy as np

from ..config import MAX_TRAILING_SILENCE
from ..utils.audio import AudioInfo


def check_trailing_silence(
    audio_info: AudioInfo,
    threshold: float = 0.01,
) -> tuple[bool, str]:
    """
    Detect trailing silence at the end of the audio.
    """

    signal = audio_info.data

    if signal.ndim == 2:
        signal = signal.mean(axis=1)

    mask = np.abs(signal) > threshold

    if not np.any(mask):
        return False, "Audio contains only silence."

    last_voice = np.where(mask)[0][-1]

    silence_samples = len(signal) - last_voice - 1

    silence_duration = silence_samples / audio_info.sample_rate

    if silence_duration > MAX_TRAILING_SILENCE:
        return (
            False,
            f"Trailing silence: {silence_duration:.2f}s."
        )

    return (
        True,
        f"Trailing silence: {silence_duration:.2f}s."
    )