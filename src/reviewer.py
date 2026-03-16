"""Novel review logic for TaleSeed."""

from __future__ import annotations

from src.llm_client import chat_json
from src.models import Novel, ReviewResult, ReviewStatus

_PASS_THRESHOLD = 6.0  # Minimum overall score to pass review

_SYSTEM_PROMPT = """\
你是一位严格、公正的文学评审专家，专门负责审核小说质量。
请从以下四个维度对小说进行评分（每项 0~10 分）：
  1. 情节连贯性（plot_score）：情节是否完整、逻辑是否自洽、转折是否合理
  2. 人物塑造（character_score）：人物性格是否鲜明、行为是否符合逻辑
  3. 语言质量（language_score）：文笔是否流畅、用词是否准确、句式是否多样
    4. 文风一致性（style_score）：文章整体文风是否统一，叙事是否连贯，是否出现明显风格/视角断裂

综合评分（score）为上述四项的加权平均，权重各 25%。
若综合评分低于 6 分，则审核不通过，需说明具体原因（rewrite_reason）。

请以 JSON 格式返回，包含以下字段：
  - plot_score: 数字（0~10）
  - character_score: 数字（0~10）
  - language_score: 数字（0~10）
  - style_score: 数字（0~10）
  - score: 数字（0~10，四项加权平均）
  - feedback: 字符串（详细的评审意见）
  - rewrite_reason: 字符串或 null（审核不通过时的重写原因）
"""


def review_novel(novel: Novel) -> ReviewResult:
    """Ask the LLM to review *novel* and return a :class:`ReviewResult`.

    The review considers plot coherence, character development, language
    quality, and style consistency.  A novel is considered to have passed
    when its overall score is at or above :data:`_PASS_THRESHOLD`.
    """
    user_prompt = (
        f"小说标题：《{novel.title}》\n"
        f"作品编号：{novel.style.value}\n\n"
        f"小说正文：\n{novel.content}"
    )

    data = chat_json(_SYSTEM_PROMPT, user_prompt, temperature=0.1)

    plot_score = float(data.get("plot_score", 5))
    character_score = float(data.get("character_score", 5))
    language_score = float(data.get("language_score", 5))
    style_score = float(data.get("style_score", 5))
    score = float(
        data.get(
            "score",
            (plot_score + character_score + language_score + style_score) / 4,
        )
    )

    status = ReviewStatus.PASSED if score >= _PASS_THRESHOLD else ReviewStatus.FAILED
    rewrite_reason: str | None = data.get("rewrite_reason") or None
    if status == ReviewStatus.FAILED and not rewrite_reason:
        rewrite_reason = "综合评分低于 6 分，整体质量不达标，需要重写。"

    return ReviewResult(
        status=status,
        score=score,
        plot_score=plot_score,
        character_score=character_score,
        language_score=language_score,
        style_score=style_score,
        feedback=data.get("feedback", ""),
        rewrite_reason=rewrite_reason if status == ReviewStatus.FAILED else None,
    )
