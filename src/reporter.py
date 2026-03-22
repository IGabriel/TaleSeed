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
    novel_paths = _save_novel_markdowns(report, out)

    md_path.write_text(generate_report(report), encoding="utf-8")
    json_path.write_text(
        json.dumps(report.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return md_path, json_path


def _save_novel_markdowns(report: Report, output_dir: Path) -> list[Path]:
    """Write each novel into an individual Markdown file.

    Files are written into *output_dir* as:
        novel_01.md .. novel_10.md
    """

    paths: list[Path] = []
    for idx, record in enumerate(report.records, start=1):
        novel = record.novel
        review = record.review

        path = output_dir / f"novel_{idx:02d}.md"
        content = "\n".join(
            [
                f"# 《{novel.title}》",
                "",
                f"- **作品编号**：{novel.style.value}",
                f"- **综合评分**：{review.score:.1f} / 10（{review.status.value}）",
                f"- **创作尝试次数**：{record.total_attempts}",
                "",
                "## 编写思路",
                "",
                novel.writing_approach or "（无）",
                "",
                "## 正文",
                "",
                novel.content.strip(),
                "",
            ]
        )
        path.write_text(content, encoding="utf-8")
        paths.append(path)

    return paths
