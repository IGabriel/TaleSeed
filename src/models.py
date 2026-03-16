"""Data models for TaleSeed novel generator."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class NovelStyle(str, Enum):
    """Ten distinctly different novel styles."""

    ROMANCE = "浪漫爱情"
    SCIFI = "科幻冒险"
    MYSTERY = "悬疑推理"
    FANTASY = "奇幻魔法"
    HISTORICAL = "历史武侠"
    URBAN = "都市言情"
    XIANXIA = "玄幻修仙"
    HORROR = "恐怖惊悚"
    CAMPUS = "青春校园"
    REALISM = "现实主义"


class ReviewStatus(str, Enum):
    """Review outcome for a novel."""

    PASSED = "通过"
    FAILED = "未通过"


class Novel(BaseModel):
    """A generated novel."""

    style: NovelStyle
    title: str = Field(description="Novel title")
    content: str = Field(description="Full novel content")
    writing_approach: str = Field(description="Writing approach and creative ideas")
    attempt: int = Field(default=1, description="Which generation attempt (1-indexed)")


class ReviewResult(BaseModel):
    """Result of reviewing a novel."""

    status: ReviewStatus
    score: float = Field(ge=0, le=10, description="Overall quality score (0–10)")
    plot_score: float = Field(ge=0, le=10, description="Plot coherence score")
    character_score: float = Field(ge=0, le=10, description="Character development score")
    language_score: float = Field(ge=0, le=10, description="Language quality score")
    style_score: float = Field(ge=0, le=10, description="Style consistency score")
    feedback: str = Field(description="Detailed review feedback")
    rewrite_reason: Optional[str] = Field(
        default=None,
        description="Reason for requiring a rewrite (only set when status is FAILED)",
    )


class NovelRecord(BaseModel):
    """Full record of a novel and its review history."""

    novel: Novel
    review: ReviewResult
    rewrite_history: list[Novel] = Field(
        default_factory=list,
        description="Previous failed versions before the final accepted version",
    )

    @property
    def total_attempts(self) -> int:
        return len(self.rewrite_history) + 1


class Report(BaseModel):
    """Final generation report."""

    seed: str = Field(description="The original story idea / brain-spark")
    records: list[NovelRecord] = Field(description="One record per novel style")

    def to_markdown(self) -> str:
        """Render the report as a Markdown string."""
        lines: list[str] = [
            "# TaleSeed 小说生成报告",
            "",
            f"**初始脑洞**：{self.seed}",
            "",
            "---",
            "",
        ]

        for idx, record in enumerate(self.records, start=1):
            novel = record.novel
            review = record.review

            lines += [
                f"## {idx}. 《{novel.title}》",
                "",
                f"- **编写风格**：{novel.style.value}",
                f"- **审核状态**：{review.status.value}",
                f"- **综合评分**：{review.score:.1f} / 10",
                f"  - 情节连贯性：{review.plot_score:.1f}",
                f"  - 人物塑造：{review.character_score:.1f}",
                f"  - 语言质量：{review.language_score:.1f}",
                f"  - 风格一致性：{review.style_score:.1f}",
                f"- **创作尝试次数**：{record.total_attempts}",
                "",
                "### 内容摘要",
                "",
                _summarise(novel.content),
                "",
                "### 编写思路",
                "",
                novel.writing_approach,
                "",
                "### 审核意见",
                "",
                review.feedback,
                "",
                "---",
                "",
            ]

        return "\n".join(lines)


def _summarise(content: str, max_chars: int = 300) -> str:
    """Return a short excerpt / first paragraph of *content*."""
    first_para = content.split("\n\n")[0].strip()
    if len(first_para) <= max_chars:
        return first_para
    return first_para[:max_chars] + "……"
