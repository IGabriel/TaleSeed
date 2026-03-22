"""Novel generation logic for TaleSeed.

This module supports a multi-step creation pipeline for each novel:

1) Decide writing technique
2) Evaluate technique; retry if unsuitable
3) Decide main characters
4) Evaluate characters; retry if unsuitable
5) Decide outline
6) Evaluate outline; retry if unsuitable
7) Draft the novel according to the outline (long-form, ~10k chars)

The final quality evaluation (step 8) is performed by :mod:`src.reviewer`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from src.llm_client import chat, chat_json
from src.models import Novel, NovelStyle

_SLOT_INDEX: dict[NovelStyle, int] = {style: idx for idx, style in enumerate(NovelStyle, start=1)}

_TARGET_CHARS = 10_000
_MIN_CHARS = 9_000
_MAX_PLAN_RETRIES = 3


@dataclass(frozen=True)
class NovelPlan:
    """Planning artifacts used to draft and rewrite a long-form novel."""

    slot_no: int
    technique: str
    characters: list[dict[str, str]]
    outline: list[dict[str, Any]]
    title: str


_SYSTEM_NOVELIST = """\
你是一位经验丰富的职业小说家，擅长将一个脑洞写成结构完整、人物立体、冲突强烈、细节充足的长篇小说。
要求：
1) 每篇小说必须与其他 9 篇明显不同（题材/设定/叙事角度/文风/结构至少两项显著差异）。
2) 以中文输出，避免流水账；多用场景与行动推进，少用空泛概括。
3) 按给定写作手法、主要角色、章节大纲进行创作，保证线索回收。
4) 单次输出只输出要求的内容，不要解释，不要加 JSON。
"""

_SYSTEM_PLANNER = """\
你是一位小说创作总编，负责在写作前完成严谨的策划：写作手法、角色设定、章节大纲。
你会优先选择可支撑约 1 万字篇幅的方案，并确保与同一脑洞的其他小说风格差异明显。
所有输出必须是 JSON 对象，字段必须齐全。
"""

_SYSTEM_EVALUATOR = """\
你是一位严格的文学策划审核员，只负责评估“写作方案/角色设定/大纲”是否适合写成长篇小说。
你会关注：可写性、冲突强度、人物动机、结构完整性、可扩展到约 1 万字、与其他槽位差异。
所有输出必须是 JSON 对象。
"""


def _count_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text or ""))


def _slot_no(style: NovelStyle) -> int:
    return _SLOT_INDEX[style]


def develop_plan(
    seed: str,
    style: NovelStyle,
    *,
    max_retries: int = _MAX_PLAN_RETRIES,
) -> NovelPlan:
    """Develop and validate a plan (technique/characters/outline) for one novel."""

    slot_no = _slot_no(style)

    technique = ""
    technique_feedback = ""
    for _ in range(max(1, max_retries)):
        user_prompt = (
            f"初始脑洞：{seed}\n\n"
            f"目标：第 {slot_no}/10 篇小说（必须与其他 9 篇明显不同）。\n"
            "请给出一个可支撑约 1 万字的写作手法方案，并输出 JSON：\n"
            "{\n"
            '  "technique": "...",\n'
            '  "difference_points": ["...", "..."],\n'
            '  "style_notes": "叙事视角/节奏/语言策略/结构安排等",\n'
            '  "proposed_title": "..."\n'
            "}\n"
            + (f"\n上一次评估未通过的改进建议：{technique_feedback}\n" if technique_feedback else "")
        )
        user_prompt += (
            "\n约束：technique/style_notes/proposed_title 字段必须简短；"
            "不要输出正文片段、长段落或多余字段。"
        )
        data = chat_json(_SYSTEM_PLANNER, user_prompt, temperature=0.3)
        technique = str(data.get("technique", "")).strip()
        proposed_title = str(data.get("proposed_title", "")).strip() or "无题"

        eval_prompt = (
            f"初始脑洞：{seed}\n"
            f"槽位：第 {slot_no}/10\n"
            f"写作手法：{technique}\n"
            "请评估是否适合写成长篇（约 1 万字），并输出 JSON：\n"
            "{\n"
            '  "passed": true/false,\n'
            '  "score": 0-10,\n'
            '  "feedback": "...",\n'
            '  "improvements": ["...", "..."]\n'
            "}\n"
        )
        ev = chat_json(_SYSTEM_EVALUATOR, eval_prompt, temperature=0.1)
        passed = bool(ev.get("passed"))
        technique_feedback = str(ev.get("feedback", "")).strip()
        if passed and technique:
            title = proposed_title
            break
    else:
        title = "无题"

    characters: list[dict[str, str]] = []
    character_feedback = ""
    for _ in range(max(1, max_retries)):
        user_prompt = (
            f"初始脑洞：{seed}\n\n"
            f"槽位：第 {slot_no}/10\n"
            f"写作手法：{technique}\n\n"
            "请敲定主要角色设定（4~6 名，含主角/对手/关键配角），输出 JSON：\n"
            "{\n"
            '  "characters": [\n'
            "    {\n"
            '      "name": "...",\n'
            '      "role": "主角/对手/配角",\n'
            '      "goal": "...",\n'
            '      "flaw": "...",\n'
            '      "arc": "..."\n'
            "    }\n"
            "  ],\n"
            '  "relationships": "主要人物关系与张力"\n'
            "}\n"
            + (f"\n上一次评估未通过的改进建议：{character_feedback}\n" if character_feedback else "")
        )
        user_prompt += "\n约束：每个字段尽量短句；不要输出任何角色小传长文或正文试写。"
        data = chat_json(_SYSTEM_PLANNER, user_prompt, temperature=0.3)
        raw_chars = data.get("characters") or []
        if isinstance(raw_chars, list):
            characters = [
                {
                    "name": str(item.get("name", "")).strip(),
                    "role": str(item.get("role", "")).strip(),
                    "goal": str(item.get("goal", "")).strip(),
                    "flaw": str(item.get("flaw", "")).strip(),
                    "arc": str(item.get("arc", "")).strip(),
                }
                for item in raw_chars
                if isinstance(item, dict)
            ]

        eval_prompt = (
            f"初始脑洞：{seed}\n"
            f"槽位：第 {slot_no}/10\n"
            f"写作手法：{technique}\n"
            f"角色设定：{characters}\n"
            "请评估角色是否支撑长篇冲突与人物成长，并输出 JSON：\n"
            "{\n"
            '  "passed": true/false,\n'
            '  "score": 0-10,\n'
            '  "feedback": "...",\n'
            '  "improvements": ["...", "..."]\n'
            "}\n"
        )
        ev = chat_json(_SYSTEM_EVALUATOR, eval_prompt, temperature=0.1)
        passed = bool(ev.get("passed"))
        character_feedback = str(ev.get("feedback", "")).strip()
        if passed and characters:
            break

    outline: list[dict[str, Any]] = []
    outline_feedback = ""
    for _ in range(max(1, max_retries)):
        user_prompt = (
            f"初始脑洞：{seed}\n\n"
            f"槽位：第 {slot_no}/10\n"
            f"写作手法：{technique}\n\n"
            f"主要角色：{characters}\n\n"
            f"目标长度：约 {_TARGET_CHARS} 字\n"
            "请敲定章节大纲（建议 8~12 章），输出 JSON：\n"
            "{\n"
            '  "title": "最终小说标题",\n'
            '  "outline": [\n'
            "    {\n"
            '      "chapter": 1,\n'
            '      "chapter_title": "...",\n'
            '      "beats": ["关键事件1", "关键事件2"],\n'
            '      "turning_point": "本章转折",\n'
            '      "focus": "本章聚焦的人物/冲突",\n'
            '      "target_chars": 900\n'
            "    }\n"
            "  ],\n"
            '  "ending": "结局与主题回收"\n'
            "}\n"
            + (f"\n上一次评估未通过的改进建议：{outline_feedback}\n" if outline_feedback else "")
        )
        user_prompt += (
            "\n约束：outline 只写章节标题与要点，beats 每章 3~6 条短句；"
            "禁止输出任何正文内容或长篇叙述。"
        )
        data = chat_json(_SYSTEM_PLANNER, user_prompt, temperature=0.3)
        title = str(data.get("title", "")).strip() or title
        raw_outline = data.get("outline") or []
        if isinstance(raw_outline, list):
            outline = [item for item in raw_outline if isinstance(item, dict)]

        eval_prompt = (
            f"初始脑洞：{seed}\n"
            f"槽位：第 {slot_no}/10\n"
            f"写作手法：{technique}\n"
            f"主要角色：{characters}\n"
            f"章节大纲：{outline}\n"
            f"目标长度：约 {_TARGET_CHARS} 字\n"
            "请评估大纲是否可写、结构完整、冲突递进、结局回收，并输出 JSON：\n"
            "{\n"
            '  "passed": true/false,\n'
            '  "score": 0-10,\n'
            '  "feedback": "...",\n'
            '  "improvements": ["...", "..."]\n'
            "}\n"
        )
        ev = chat_json(_SYSTEM_EVALUATOR, eval_prompt, temperature=0.1)
        passed = bool(ev.get("passed"))
        outline_feedback = str(ev.get("feedback", "")).strip()
        if passed and outline:
            break

    return NovelPlan(
        slot_no=slot_no,
        technique=technique,
        characters=characters,
        outline=outline,
        title=title,
    )


def draft_novel(
    seed: str,
    style: NovelStyle,
    plan: NovelPlan,
    *,
    attempt: int = 1,
    rewrite_reason: str | None = None,
) -> Novel:
    """Draft a long-form novel (~10k chars) from an existing plan.

    This function implements step #7 and can be called repeatedly for rewrites
    while keeping the plan fixed.
    """

    outline = plan.outline or []
    chapters = outline if outline else [
        {
            "chapter": 1,
            "chapter_title": "正文",
            "beats": [],
            "turning_point": "",
            "focus": "",
            "target_chars": _TARGET_CHARS,
        }
    ]

    content_parts: list[str] = []
    previous_tail = ""

    for idx, chapter in enumerate(chapters, start=1):
        chapter_no = int(chapter.get("chapter") or idx)
        chapter_title = str(chapter.get("chapter_title") or f"第{chapter_no}章").strip()
        target_chars = int(chapter.get("target_chars") or max(800, _TARGET_CHARS // max(1, len(chapters))))
        beats = chapter.get("beats") or []
        turning_point = str(chapter.get("turning_point") or "").strip()
        focus = str(chapter.get("focus") or "").strip()

        user_prompt = (
            f"初始脑洞：{seed}\n"
            f"槽位：第 {plan.slot_no}/10\n"
            f"写作手法：{plan.technique}\n\n"
            f"主要角色：{plan.characters}\n\n"
            f"全书大纲（供参考）：{plan.outline}\n\n"
            f"现在请写第 {chapter_no} 章：{chapter_title}\n"
            f"本章要点：{beats}\n"
            f"本章聚焦：{focus}\n"
            f"本章转折：{turning_point}\n\n"
            f"长度要求：约 {target_chars} 字（尽量接近；不得少于 {max(600, int(target_chars * 0.7))} 字）。\n"
            "输出要求：只输出本章正文，可包含小节分隔与适量对话，不要输出章外说明。\n"
        )
        if previous_tail:
            user_prompt += f"\n上一章结尾（保持衔接与文风一致）：\n{previous_tail}\n"
        if attempt > 1 and rewrite_reason:
            user_prompt += f"\n这是重写稿：请根据以下问题进行改写与增强：{rewrite_reason}\n"

        chapter_text = chat(_SYSTEM_NOVELIST, user_prompt, temperature=0.9)
        chapter_text = (chapter_text or "").strip()

        heading = f"\n\n## 第{chapter_no}章 {chapter_title}\n\n"
        content_parts.append(heading + chapter_text)
        previous_tail = chapter_text[-800:]

    content = "".join(content_parts).strip()

    # If still too short, add a final "extra scenes" section to reach the minimum.
    extra_rounds = 0
    while _count_chars(content) < _MIN_CHARS and extra_rounds < 2:
        extra_rounds += 1
        deficit = _MIN_CHARS - _count_chars(content)
        extra_target = min(1600, max(800, deficit))
        extra_prompt = (
            f"初始脑洞：{seed}\n"
            f"槽位：第 {plan.slot_no}/10\n"
            f"写作手法：{plan.technique}\n"
            f"主要角色：{plan.characters}\n"
            f"全书大纲：{plan.outline}\n\n"
            "当前正文已写完但篇幅不足，请补写一个承上启下的场景或结尾余韵，必须与既有内容一致。\n"
            f"补写长度：约 {extra_target} 字。\n"
            "输出要求：只输出补写正文，不要复述前文，不要解释。\n\n"
            f"当前正文末尾片段：\n{content[-1200:]}\n"
        )
        extra = chat(_SYSTEM_NOVELIST, extra_prompt, temperature=0.9).strip()
        content += "\n\n" + extra

    writing_approach = (
        "写作手法：" + (plan.technique or "") + "\n\n"
        "主要角色：" + ", ".join([c.get("name", "") for c in plan.characters if c.get("name")]) + "\n\n"
        "结构大纲：" + "；".join(
            [str(ch.get("chapter_title") or "") for ch in (plan.outline or [])][:8]
        )
    ).strip()

    return Novel(
        style=style,
        title=plan.title or "无题",
        content=content,
        writing_approach=writing_approach,
        attempt=attempt,
    )


def generate_novel(seed: str, style: NovelStyle, attempt: int = 1) -> Novel:
    """Generate a single novel.

    This convenience wrapper builds a plan and drafts the novel once. For
    rewrite loops that should keep the plan fixed, prefer calling
    :func:`develop_plan` once and then :func:`draft_novel` multiple times.
    """

    plan = develop_plan(seed, style)
    return draft_novel(seed, style, plan, attempt=attempt)


def generate_all_novels(seed: str) -> list[Novel]:
    """Generate one novel for each of the ten styles.

    Returns a list of ten :class:`Novel` objects in the order defined by
    :class:`NovelStyle`.
    """
    return [generate_novel(seed, style) for style in NovelStyle]
