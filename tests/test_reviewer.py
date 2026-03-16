"""Tests for the reviewer module (mocked LLM)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.models import Novel, NovelStyle, ReviewStatus
from src.reviewer import review_novel


def _make_novel(title: str = "测试") -> Novel:
    return Novel(
        style=NovelStyle.ROMANCE,
        title=title,
        content="内容" * 200,
        writing_approach="思路",
    )


def _mock_passed(_s, _u, **_kw) -> dict:
    return {
        "plot_score": 8,
        "character_score": 7,
        "language_score": 8,
        "style_score": 9,
        "score": 8.0,
        "feedback": "写得很好！",
        "rewrite_reason": None,
    }


def _mock_failed(_s, _u, **_kw) -> dict:
    return {
        "plot_score": 4,
        "character_score": 3,
        "language_score": 4,
        "style_score": 5,
        "score": 4.0,
        "feedback": "整体质量较差。",
        "rewrite_reason": "情节混乱，人物苍白。",
    }


class TestReviewNovel:
    def test_passed_review(self):
        with patch("src.reviewer.chat_json", side_effect=_mock_passed):
            result = review_novel(_make_novel())

        assert result.status == ReviewStatus.PASSED
        assert result.score == 8.0
        assert result.rewrite_reason is None

    def test_failed_review(self):
        with patch("src.reviewer.chat_json", side_effect=_mock_failed):
            result = review_novel(_make_novel())

        assert result.status == ReviewStatus.FAILED
        assert result.score == 4.0
        assert result.rewrite_reason is not None
        assert len(result.rewrite_reason) > 0

    def test_failed_review_no_reason_gets_default(self):
        def _no_reason(_s, _u, **_kw) -> dict:
            return {
                "plot_score": 3,
                "character_score": 3,
                "language_score": 3,
                "style_score": 3,
                "score": 3.0,
                "feedback": "差。",
                "rewrite_reason": None,
            }

        with patch("src.reviewer.chat_json", side_effect=_no_reason):
            result = review_novel(_make_novel())

        assert result.status == ReviewStatus.FAILED
        assert result.rewrite_reason is not None

    def test_score_fallback_from_subscores(self):
        """If the LLM omits 'score', it should be computed from sub-scores."""

        def _no_overall(_s, _u, **_kw) -> dict:
            return {
                "plot_score": 8,
                "character_score": 8,
                "language_score": 8,
                "style_score": 8,
                "feedback": "好。",
                "rewrite_reason": None,
            }

        with patch("src.reviewer.chat_json", side_effect=_no_overall):
            result = review_novel(_make_novel())

        assert result.score == pytest.approx(8.0)
        assert result.status == ReviewStatus.PASSED
