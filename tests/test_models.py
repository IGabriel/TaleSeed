"""Tests for data models."""

from __future__ import annotations

import pytest

from src.models import (
    Novel,
    NovelRecord,
    NovelStyle,
    Report,
    ReviewResult,
    ReviewStatus,
    _summarise,
)


class TestNovelStyle:
    def test_all_five_styles_exist(self):
        styles = list(NovelStyle)
        assert len(styles) == 10

    def test_style_values_are_chinese(self):
        for style in NovelStyle:
            assert len(style.value) > 0


class TestNovel:
    def test_create_novel(self):
        novel = Novel(
            style=NovelStyle.SLOT_1,
            title="测试标题",
            content="测试内容",
            writing_approach="测试思路",
        )
        assert novel.title == "测试标题"
        assert novel.attempt == 1

    def test_attempt_defaults_to_one(self):
        novel = Novel(
            style=NovelStyle.SLOT_2,
            title="T",
            content="C",
            writing_approach="A",
        )
        assert novel.attempt == 1


class TestReviewResult:
    def _make_review(self, score: float, status: ReviewStatus) -> ReviewResult:
        return ReviewResult(
            status=status,
            score=score,
            plot_score=score,
            character_score=score,
            language_score=score,
            style_score=score,
            feedback="okay",
        )

    def test_passed_review(self):
        r = self._make_review(7.5, ReviewStatus.PASSED)
        assert r.status == ReviewStatus.PASSED
        assert r.rewrite_reason is None

    def test_failed_review_has_rewrite_reason(self):
        r = ReviewResult(
            status=ReviewStatus.FAILED,
            score=4.0,
            plot_score=4.0,
            character_score=4.0,
            language_score=4.0,
            style_score=4.0,
            feedback="bad",
            rewrite_reason="情节混乱",
        )
        assert r.rewrite_reason == "情节混乱"

    def test_score_bounds(self):
        with pytest.raises(Exception):
            ReviewResult(
                status=ReviewStatus.PASSED,
                score=11.0,  # out of bounds
                plot_score=5,
                character_score=5,
                language_score=5,
                style_score=5,
                feedback="",
            )


class TestNovelRecord:
    def _make_novel(self, attempt: int = 1) -> Novel:
        return Novel(
            style=NovelStyle.SLOT_3,
            title="T",
            content="C",
            writing_approach="A",
            attempt=attempt,
        )

    def _make_review(self) -> ReviewResult:
        return ReviewResult(
            status=ReviewStatus.PASSED,
            score=7.0,
            plot_score=7,
            character_score=7,
            language_score=7,
            style_score=7,
            feedback="good",
        )

    def test_total_attempts_no_history(self):
        record = NovelRecord(novel=self._make_novel(), review=self._make_review())
        assert record.total_attempts == 1

    def test_total_attempts_with_history(self):
        record = NovelRecord(
            novel=self._make_novel(attempt=3),
            review=self._make_review(),
            rewrite_history=[self._make_novel(1), self._make_novel(2)],
        )
        assert record.total_attempts == 3


class TestReport:
    def _make_report(self) -> Report:
        novel = Novel(
            style=NovelStyle.SLOT_4,
            title="魔法传说",
            content="第一段\n\n第二段",
            writing_approach="以魔法为核心",
        )
        review = ReviewResult(
            status=ReviewStatus.PASSED,
            score=8.0,
            plot_score=8,
            character_score=8,
            language_score=8,
            style_score=8,
            feedback="非常出色",
        )
        return Report(seed="一粒魔法种子", records=[NovelRecord(novel=novel, review=review)])

    def test_to_markdown_contains_title(self):
        report = self._make_report()
        md = report.to_markdown()
        assert "魔法传说" in md

    def test_to_markdown_contains_seed(self):
        report = self._make_report()
        md = report.to_markdown()
        assert "一粒魔法种子" in md

    def test_to_markdown_contains_style(self):
        report = self._make_report()
        md = report.to_markdown()
        assert NovelStyle.SLOT_4.value in md

    def test_to_markdown_contains_scores(self):
        report = self._make_report()
        md = report.to_markdown()
        assert "8.0" in md


class TestSummarise:
    def test_short_content_unchanged(self):
        text = "短文本"
        assert _summarise(text) == text

    def test_long_content_truncated(self):
        text = "a" * 500
        result = _summarise(text)
        assert len(result) < 500
        assert result.endswith("……")

    def test_uses_first_paragraph(self):
        text = "第一段内容\n\n第二段内容"
        result = _summarise(text)
        assert "第一段内容" in result
        assert "第二段内容" not in result
