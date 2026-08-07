"""
Utility functions for reading audio files and extracting metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf


@dataclass(slots=True)
class AudioInfo:
    """
    Stores useful metadata extracted from an audio file.
    """

    path: Path
    sample_rate: int
    channels: int
    duration: float
    frames: int
    subtype: str
    format: str
    peak: float
    data: np.ndarray


def read_audio_info(audio_path: Path) -> AudioInfo:
    """
    Read an audio file and return its metadata.

    Parameters
    ----------
    audio_path : Path
        Path to the audio file.

    Returns
    -------
    AudioInfo
        Metadata describing the audio.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.

    RuntimeError
        If the file cannot be read.
    """

    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"File not found: {audio_path}")

    try:
        data, sample_rate = sf.read(audio_path)

        info = sf.info(audio_path)

    except Exception as exc:
        raise RuntimeError(
            f"Unable to read audio file: {audio_path}"
        ) from exc

    if data.ndim == 1:
        channels = 1
    else:
        channels = data.shape[1]

    duration = len(data) / sample_rate

    peak = float(np.max(np.abs(data)))

    return AudioInfo(
    path=audio_path,
    sample_rate=sample_rate,
    channels=channels,
    duration=duration,
    frames=info.frames,
    subtype=info.subtype,
    format=info.format,
    peak=peak,
    data=data,
)