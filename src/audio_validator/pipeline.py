"""
Validation pipeline.
"""

from pathlib import Path

from .checks.channels_check import check_channels
from .checks.duration_check import check_duration
from .checks.file_check import (
    check_file_exists,
    check_file_readable,
)
from .checks.format_check import check_audio_format
from .checks.peak_check import check_peak
from .checks.samplerate_check import check_sample_rate
from .checks.silence_check import check_trailing_silence

from .utils.audio import read_audio_info


class ValidationPipeline:

    def validate(self, audio_path: Path) -> list[tuple[str, bool, str]]:
        """
        Validate one audio file.
        """

        results = []

        status, message = check_file_exists(audio_path)
        results.append(("EXISTS", status, message))

        if not status:
            return results

        status, message = check_file_readable(audio_path)
        results.append(("READABLE", status, message))

        if not status:
            return results

        status, message = check_audio_format(audio_path)
        results.append(("FORMAT", status, message))

        info = read_audio_info(audio_path)

        checks = [
            ("SAMPLE", check_sample_rate),
            ("CHANNELS", check_channels),
            ("DURATION", check_duration),
            ("PEAK", check_peak),
            ("SILENCE", check_trailing_silence),
        ]

        for name, check in checks:

            status, message = check(info)

            results.append(
                (
                    name,
                    status,
                    message,
                )
            )

        return results