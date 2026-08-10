from pathlib import Path

from .checks.duplicate_check import check_duplicates
from .checks.transcript_check import check_transcripts
from .pipeline import ValidationPipeline
from .report import ValidationReport
from .utils.audio import read_audio_info


def main() -> None:

    pipeline = ValidationPipeline()
    report = ValidationReport()

    dataset_root = Path("eval/audio_validator/dataset")
    manifest_path = dataset_root / "train.jsonl"

    # ------------------------------------------------------------------
    # Transcript check
    # ------------------------------------------------------------------

    transcript_results = {
        item["audio"]: item
        for item in check_transcripts(
            manifest_path,
            dataset_root,
        )
    }

    # ------------------------------------------------------------------
    # Duplicate check
    # ------------------------------------------------------------------

    audio_files = sorted(dataset_root.joinpath("audio").rglob("*"))

    audio_files = [
        file
        for file in audio_files
        if file.is_file()
    ]

    duplicate_results = check_duplicates(audio_files)

    # ------------------------------------------------------------------
    # Audio validation
    # ------------------------------------------------------------------

    for audio in audio_files:

        validation = pipeline.validate(audio)

        info = read_audio_info(audio)

        status = "PASS"
        warnings = []
        errors = []

        for check, passed, message in validation:

            if not passed:
                status = "FAIL"
                errors.append(message)

        relative_path = audio.relative_to(dataset_root).as_posix()

        print(relative_path)
        print(transcript_results.keys())

        transcript = transcript_results.get(
            relative_path,
            {},
        )

        transcript_ok = (
            "Yes"
            if transcript.get("status", False)
            else "No"
        )

        if transcript_ok == "No":
            status = "FAIL"
            errors.append(transcript.get("message", ""))

        duplicate_ok, duplicate_msg = duplicate_results[audio]

        duplicate = "No"

        if not duplicate_ok:
            duplicate = "Yes"
            status = "FAIL"
            errors.append(duplicate_msg)

        clipping = "No"

        for check, passed, message in validation:
            if check == "PEAK" and not passed:
                clipping = "Yes"

        silence = "No"

        for check, passed, message in validation:
            if check == "SILENCE" and not passed:
                silence = "Yes"

        report.add_result(
            file_path=audio.relative_to(dataset_root),
            status=status,
            audio_format=info.format,
            sample_rate=info.sample_rate,
            channels="Mono" if info.channels == 1 else "Stereo",
            duration=info.duration,
            clipping=clipping,
            silence=silence,
            transcript=transcript_ok,
            duplicate=duplicate,
            warnings="; ".join(warnings),
            errors="; ".join(errors),
        )

    # ------------------------------------------------------------------
    # Save reports
    # ------------------------------------------------------------------

    report.save_reports()

    print("\nReports generated successfully.")
    print(" - reports/validation_report.csv")
    print(" - reports/invalid_files.csv")
    print(" - reports/validation_summary.txt")


if __name__ == "__main__":
    main()