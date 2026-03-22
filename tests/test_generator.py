"""Tests for the generator module.

The generator now performs multi-step planning and long-form drafting. These
tests patch the higher-level helpers to keep unit tests fast and deterministic.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.generator import NovelPlan, generate_all_novels, generate_novel
from src.models import Novel, NovelStyle


def _make_plan(style: NovelStyle) -> NovelPlan:
    return NovelPlan(
        slot_no=1,
        technique="测试写作手法",
        characters=[{"name": "测试角色", "role": "主角", "goal": "", "flaw": "", "arc": ""}],
        outline=[{"chapter": 1, "chapter_title": "开端", "beats": [], "turning_point": "", "focus": "", "target_chars": 9000}],
        title="测试小说",
    )


def _make_novel(style: NovelStyle, attempt: int = 1) -> Novel:
    return Novel(
        style=style,
        title="测试小说",
        content="这是测试内容。" * 600,  # long enough
        writing_approach="以测试为核心的创作思路。",
        attempt=attempt,
    )


class TestGenerateNovel:
    def test_returns_novel(self):
        with (
            patch("src.generator.develop_plan", side_effect=lambda seed, style, **_: _make_plan(style)),
            patch("src.generator.draft_novel", side_effect=lambda seed, style, plan, **kw: _make_novel(style, kw.get("attempt", 1))),
        ):
            novel = generate_novel("一颗流星", NovelStyle.SLOT_2)

        assert isinstance(novel, Novel)
        assert novel.style == NovelStyle.SLOT_2
        assert novel.title == "测试小说"
        assert novel.attempt == 1

    def test_attempt_is_recorded(self):
        with (
            patch("src.generator.develop_plan", side_effect=lambda seed, style, **_: _make_plan(style)),
            patch("src.generator.draft_novel", side_effect=lambda seed, style, plan, **kw: _make_novel(style, kw.get("attempt", 1))),
        ):
            novel = generate_novel("一颗流星", NovelStyle.SLOT_1, attempt=2)

        assert novel.attempt == 2

    def test_missing_title_defaults(self):
        # Title handling now lives in the plan; ensure draft_novel receives plan.title.
        def _plan_without_title(style: NovelStyle) -> NovelPlan:
            p = _make_plan(style)
            return NovelPlan(
                slot_no=p.slot_no,
                technique=p.technique,
                characters=p.characters,
                outline=p.outline,
                title="",
            )

        with (
            patch("src.generator.develop_plan", side_effect=lambda seed, style, **_: _plan_without_title(style)),
            patch("src.generator.draft_novel", side_effect=lambda seed, style, plan, **kw: Novel(
                style=style,
                title=plan.title or "无题",
                content="内容" * 100,
                writing_approach="思路",
                attempt=kw.get("attempt", 1),
            )),
        ):
            novel = generate_novel("seed", NovelStyle.SLOT_3)

        assert novel.title == "无题"


class TestGenerateAllNovels:
    def test_returns_five_novels(self):
        with (
            patch("src.generator.develop_plan", side_effect=lambda seed, style, **_: _make_plan(style)),
            patch("src.generator.draft_novel", side_effect=lambda seed, style, plan, **kw: _make_novel(style, kw.get("attempt", 1))),
        ):
            novels = generate_all_novels("一颗流星")

        assert len(novels) == 10

    def test_all_styles_covered(self):
        with (
            patch("src.generator.develop_plan", side_effect=lambda seed, style, **_: _make_plan(style)),
            patch("src.generator.draft_novel", side_effect=lambda seed, style, plan, **kw: _make_novel(style, kw.get("attempt", 1))),
        ):
            novels = generate_all_novels("一颗流星")

        styles = {n.style for n in novels}
        assert styles == set(NovelStyle)
