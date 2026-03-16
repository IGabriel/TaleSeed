"""Report generation for TaleSeed."""

from __future__ import annotations

import json
from pathlib import Path

from src.models import Report


def generate_report(report: Report) -> str:
    """Return the Markdown representation of *report*."""
    return report.to_markdown()


def save_report(report: Report, output_dir: str | Path = ".") -> tuple[Path, Path]:
    """Write the report to *output_dir* in both Markdown and JSON formats.

    Parameters
    ----------
    report:
        The completed :class:`~src.models.Report` to persist.
    output_dir:
        Directory where output files will be written.  Created if it does not
        exist.

    Returns
    -------
    tuple[Path, Path]
        Paths to the saved Markdown and JSON files respectively.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    md_path = out / "report.md"
    json_path = out / "report.json"

    md_path.write_text(generate_report(report), encoding="utf-8")
    json_path.write_text(
        json.dumps(report.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return md_path, json_path
