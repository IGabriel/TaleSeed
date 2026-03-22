"""Tests for the reporter module."""

from __future__ import annotations

import json
from pathlib import Path

from src.models import Novel, NovelRecord, NovelStyle, Report, ReviewResult, ReviewStatus
from src.reporter import generate_report, save_report


def _make_report(seed: str = "测试脑洞") -> Report:
    novel = Novel(
        style=NovelStyle.SLOT_5,
        title="江湖往事",
        content="刀光剑影中，\n\n一段传奇缓缓展开。",
        writing_approach="以历史为背景，融入武侠元素。",
    )
    review = ReviewResult(
        status=ReviewStatus.PASSED,
        score=7.5,
        plot_score=7,
        character_score=8,
        language_score=7,
        style_score=8,
        feedback="历史感强，人物鲜活。",
    )
    return Report(seed=seed, records=[NovelRecord(novel=novel, review=review)])


class TestGenerateReport:
    def test_returns_string(self):
        report = _make_report()
        md = generate_report(report)
        assert isinstance(md, str)
        assert len(md) > 0

    def test_contains_title(self):
        report = _make_report()
        md = generate_report(report)
        assert "江湖往事" in md

    def test_contains_seed(self):
        report = _make_report("神秘脑洞")
        md = generate_report(report)
        assert "神秘脑洞" in md


class TestSaveReport:
    def test_creates_markdown_and_json(self, tmp_path: Path):
        report = _make_report()
        md_path, json_path = save_report(report, tmp_path)

        assert md_path.exists()
        assert json_path.exists()
        assert (tmp_path / "novel_01.md").exists()

    def test_json_is_valid(self, tmp_path: Path):
        report = _make_report()
        _, json_path = save_report(report, tmp_path)

        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["seed"] == "测试脑洞"
        assert len(data["records"]) == 1

    def test_creates_output_dir_if_missing(self, tmp_path: Path):
        out_dir = tmp_path / "nested" / "output"
        report = _make_report()
        md_path, json_path = save_report(report, out_dir)

        assert out_dir.exists()
        assert md_path.exists()
        assert (out_dir / "novel_01.md").exists()
