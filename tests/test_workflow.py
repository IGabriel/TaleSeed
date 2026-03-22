"""Tests for the main workflow (mocked LLM)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from src.models import Novel, NovelStyle, Report, ReviewResult, ReviewStatus
from src.workflow import run

_SEED = "一颗流星坠入古代江湖"


def _make_novel(style: NovelStyle, attempt: int = 1) -> Novel:
    return Novel(
        style=style,
        title=f"《{style.value}》第{attempt}版",
        content="内容" * 200,
        writing_approach="思路",
        attempt=attempt,
    )


def _make_plan(_seed: str, style: NovelStyle, **_kw):
    # Minimal plan-like object for tests; workflow only passes it through.
    return {"style": style}


def _make_review(passed: bool) -> ReviewResult:
    score = 8.0 if passed else 4.0
    status = ReviewStatus.PASSED if passed else ReviewStatus.FAILED
    return ReviewResult(
        status=status,
        score=score,
        plot_score=score,
        character_score=score,
        language_score=score,
        style_score=score,
        feedback="反馈",
        rewrite_reason=None if passed else "质量不达标",
    )


class TestWorkflow:
    def test_run_returns_report(self, tmp_path: Path):
        def fake_draft(seed, style, plan, attempt=1, rewrite_reason=None):
            return _make_novel(style, attempt)

        def fake_review(novel):
            return _make_review(passed=True)

        with (
            patch("src.workflow.develop_plan", side_effect=_make_plan),
            patch("src.workflow.draft_novel", side_effect=fake_draft),
            patch("src.workflow.review_novel", side_effect=fake_review),
        ):
            report = run(_SEED, output_dir=tmp_path, verbose=False)

        assert isinstance(report, Report)
        assert len(report.records) == 10

    def test_run_covers_all_styles(self, tmp_path: Path):
        def fake_draft(seed, style, plan, attempt=1, rewrite_reason=None):
            return _make_novel(style, attempt)

        def fake_review(novel):
            return _make_review(passed=True)

        with (
            patch("src.workflow.develop_plan", side_effect=_make_plan),
            patch("src.workflow.draft_novel", side_effect=fake_draft),
            patch("src.workflow.review_novel", side_effect=fake_review),
        ):
            report = run(_SEED, output_dir=tmp_path, verbose=False)

        styles = {r.novel.style for r in report.records}
        assert styles == set(NovelStyle)

    def test_failed_review_triggers_rewrite(self, tmp_path: Path):
        """A failing review should cause one rewrite before success."""
        draft_counts: dict[NovelStyle, int] = {s: 0 for s in NovelStyle}

        def fake_draft(seed, style, plan, attempt=1, rewrite_reason=None):
            draft_counts[style] += 1
            return _make_novel(style, attempt)

        review_calls: dict[NovelStyle, int] = {s: 0 for s in NovelStyle}

        def fake_review(novel):
            review_calls[novel.style] += 1
            # Fail the first review for SLOT_1 only
            if novel.style == NovelStyle.SLOT_1 and review_calls[novel.style] == 1:
                return _make_review(passed=False)
            return _make_review(passed=True)

        with (
            patch("src.workflow.develop_plan", side_effect=_make_plan),
            patch("src.workflow.draft_novel", side_effect=fake_draft),
            patch("src.workflow.review_novel", side_effect=fake_review),
        ):
            report = run(_SEED, max_retries=3, output_dir=tmp_path, verbose=False)

        romance_record = next(r for r in report.records if r.novel.style == NovelStyle.SLOT_1)
        # Should have 1 failed attempt in history, 1 successful final
        assert len(romance_record.rewrite_history) == 1
        assert romance_record.total_attempts == 2

    def test_max_retries_respected(self, tmp_path: Path):
        """When all reviews fail, the workflow should stop after max_retries."""
        draft_counts: dict[NovelStyle, int] = {s: 0 for s in NovelStyle}

        def fake_draft(seed, style, plan, attempt=1, rewrite_reason=None):
            draft_counts[style] += 1
            return _make_novel(style, attempt)

        def fake_review(novel):
            return _make_review(passed=False)

        max_retries = 2

        with (
            patch("src.workflow.develop_plan", side_effect=_make_plan),
            patch("src.workflow.draft_novel", side_effect=fake_draft),
            patch("src.workflow.review_novel", side_effect=fake_review),
        ):
            report = run(
                _SEED, max_retries=max_retries, output_dir=tmp_path, verbose=False
            )

        for record in report.records:
            assert draft_counts[record.novel.style] == max_retries

    def test_report_files_created(self, tmp_path: Path):
        def fake_draft(seed, style, plan, attempt=1, rewrite_reason=None):
            return _make_novel(style, attempt)

        def fake_review(novel):
            return _make_review(passed=True)

        with (
            patch("src.workflow.develop_plan", side_effect=_make_plan),
            patch("src.workflow.draft_novel", side_effect=fake_draft),
            patch("src.workflow.review_novel", side_effect=fake_review),
        ):
            run(_SEED, output_dir=tmp_path, verbose=False)

        assert (tmp_path / "report.md").exists()
        assert (tmp_path / "report.json").exists()
        for idx in range(1, 11):
            assert (tmp_path / f"novel_{idx:02d}.md").exists()
