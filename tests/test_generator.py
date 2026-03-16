"""Tests for the generator module (mocked LLM)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.generator import generate_all_novels, generate_novel
from src.models import Novel, NovelStyle


def _mock_chat_json(_system: str, _user: str, **_kwargs) -> dict:
    return {
        "title": "测试小说",
        "content": "这是测试内容。" * 120,  # ~840 chars
        "writing_approach": "以测试为核心的创作思路。",
    }


class TestGenerateNovel:
    def test_returns_novel(self):
        with patch("src.generator.chat_json", side_effect=_mock_chat_json):
            novel = generate_novel("一颗流星", NovelStyle.SCIFI)

        assert isinstance(novel, Novel)
        assert novel.style == NovelStyle.SCIFI
        assert novel.title == "测试小说"
        assert novel.attempt == 1

    def test_attempt_is_recorded(self):
        with patch("src.generator.chat_json", side_effect=_mock_chat_json):
            novel = generate_novel("一颗流星", NovelStyle.ROMANCE, attempt=2)

        assert novel.attempt == 2

    def test_missing_title_defaults(self):
        def _no_title(_s, _u, **_kw):
            return {"content": "内容", "writing_approach": "思路"}

        with patch("src.generator.chat_json", side_effect=_no_title):
            novel = generate_novel("seed", NovelStyle.MYSTERY)

        assert novel.title == "无题"


class TestGenerateAllNovels:
    def test_returns_five_novels(self):
        with patch("src.generator.chat_json", side_effect=_mock_chat_json):
            novels = generate_all_novels("一颗流星")

        assert len(novels) == 10

    def test_all_styles_covered(self):
        with patch("src.generator.chat_json", side_effect=_mock_chat_json):
            novels = generate_all_novels("一颗流星")

        styles = {n.style for n in novels}
        assert styles == set(NovelStyle)
