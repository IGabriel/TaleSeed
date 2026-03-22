"""Main generation workflow for TaleSeed.

Flow
----
For each of the ten novel styles:
  1. Generate a novel from the seed idea.
  2. Review the novel with the LLM reviewer.
  3. If the review fails, rewrite and review again — up to *max_retries* times.
  4. Record the final novel and its review (regardless of whether it passed).

After all ten novels are processed, build and return a :class:`~src.models.Report`.
"""

from __future__ import annotations

import logging
from pathlib import Path

from src.generator import develop_plan, draft_novel
from src.models import NovelRecord, NovelStyle, Report
from src.reporter import save_report
from src.reviewer import review_novel

logger = logging.getLogger(__name__)

_DEFAULT_MAX_RETRIES = 3  # maximum rewrite attempts per novel


def run(
    seed: str,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    output_dir: str | Path = "output",
    verbose: bool = True,
) -> Report:
    """Run the full TaleSeed generation workflow.

    Parameters
    ----------
    seed:
        The initial story idea / brain-spark.
    max_retries:
        Maximum number of rewrite attempts per novel when a review fails.
    output_dir:
        Directory where the final report files are saved.
    verbose:
        Print progress messages to stdout when ``True``.

    Returns
    -------
    Report
        The completed report containing all novel records.
    """

    def log(msg: str) -> None:
        if verbose:
            print(msg)
        logger.info(msg)

    records: list[NovelRecord] = []

    for style in NovelStyle:
        log(f"\n{'=' * 60}")
        log(f"[生成] {style.value}")

        attempt = 1
        plan = develop_plan(seed, style, max_retries=max_retries)
        log(f"  ✓ 策划完成：写作手法/角色/大纲已敲定")

        novel = draft_novel(seed, style, plan, attempt=attempt)
        log(f"  ✓ 正文完成：《{novel.title}》（第 {attempt} 次）")

        review = review_novel(novel)
        log(
            f"  → 审核结果：{review.status.value}  评分：{review.score:.1f}/10"
        )

        rewrite_history = []

        while review.status.value == "未通过" and attempt < max_retries:
            log(f"  ✗ 需要重写：{review.rewrite_reason}")
            rewrite_history.append(novel)

            attempt += 1
            novel = draft_novel(
                seed,
                style,
                plan,
                attempt=attempt,
                rewrite_reason=review.rewrite_reason,
            )
            log(f"  ✓ 重写完成：《{novel.title}》（第 {attempt} 次）")

            review = review_novel(novel)
            log(
                f"  → 审核结果：{review.status.value}  评分：{review.score:.1f}/10"
            )

        if review.status.value == "未通过":
            log(
                f"  ! 已达最大重写次数 ({max_retries})，保留当前版本（评分 {review.score:.1f}）"
            )

        records.append(
            NovelRecord(
                novel=novel,
                review=review,
                rewrite_history=rewrite_history,
            )
        )

    report = Report(seed=seed, records=records)
    md_path, json_path = save_report(report, output_dir)

    log(f"\n{'=' * 60}")
    log(f"[完成] 报告已保存至：")
    log(f"  Markdown : {md_path}")
    log(f"  JSON     : {json_path}")

    return report
