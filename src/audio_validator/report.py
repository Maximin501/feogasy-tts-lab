"""
Validation report generation.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd


class ValidationReport:
    """
    Generate validation reports.
    """

    def __init__(self) -> None:

        self.rows: list[dict] = []

    def add_result(
        self,
        *,
        file_path: Path,
        status: str,
        audio_format: str,
        sample_rate: int,
        channels: str,
        duration: float,
        clipping: str,
        silence: str,
        transcript: str,
        duplicate: str,
        warnings: str = "",
        errors: str = "",
    ) -> None:

        self.rows.append(
            {
                "file_path": str(file_path),
                "filename": file_path.name,
                "status": status,
                "format": audio_format,
                "sample_rate": sample_rate,
                "channels": channels,
                "duration_s": round(duration, 2),
                "clipping": clipping,
                "silence": silence,
                "transcript": transcript,
                "duplicate": duplicate,
                "warnings": warnings,
                "errors": errors,
            }
        )

    def dataframe(self) -> pd.DataFrame:

        return pd.DataFrame(self.rows)

    def save_reports(
        self,
        output_dir: Path = Path("eval/audio_validator/reports"),
    ) -> None:

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        df = self.dataframe()

        report_csv = output_dir / "validation_report.csv"
        invalid_csv = output_dir / "invalid_files.csv"
        summary_txt = output_dir / "validation_summary.txt"

        df.to_csv(
            report_csv,
            index=False,
            encoding="utf-8",
        )

        df[df["status"] == "FAIL"].to_csv(
            invalid_csv,
            index=False,
            encoding="utf-8",
        )

        self._write_summary(
            df,
            summary_txt,
        )

    @staticmethod
    def _write_summary(
        df: pd.DataFrame,
        output_file: Path,
    ) -> None:

        total = len(df)

        passed = (df["status"] == "PASS").sum()

        failed = (df["status"] == "FAIL").sum()

        pass_rate = (passed / total * 100) if total else 0

        error_counter = Counter()

        warning_counter = Counter()

        for value in df["errors"]:

            if value:
                error_counter.update(
                    [v.strip() for v in value.split(";")]
                )

        for value in df["warnings"]:

            if value:
                warning_counter.update(
                    [v.strip() for v in value.split(";")]
                )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as f:

            f.write("=" * 45 + "\n")
            f.write("AUDIO VALIDATION SUMMARY\n")
            f.write("=" * 45 + "\n\n")

            f.write(f"Total files : {total}\n")
            f.write(f"Passed      : {passed}\n")
            f.write(f"Failed      : {failed}\n")
            f.write(f"Pass rate   : {pass_rate:.2f}%\n\n")

            f.write("-" * 45 + "\n")
            f.write("Failure reasons\n")
            f.write("-" * 45 + "\n")

            if error_counter:
                for key, value in error_counter.items():
                    f.write(f"{key:<30}{value}\n")
            else:
                f.write("None\n")

            f.write("\n")

            f.write("-" * 45 + "\n")
            f.write("Warning reasons\n")
            f.write("-" * 45 + "\n")

            if warning_counter:
                for key, value in warning_counter.items():
                    f.write(f"{key:<30}{value}\n")
            else:
                f.write("None\n")

            f.write("\n")
            f.write("=" * 45 + "\n")