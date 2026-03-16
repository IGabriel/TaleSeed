"""Novel generation logic for TaleSeed."""

from __future__ import annotations

from src.llm_client import chat_json
from src.models import Novel, NovelStyle

_SLOT_INDEX: dict[NovelStyle, int] = {style: idx for idx, style in enumerate(NovelStyle, start=1)}

_SYSTEM_PROMPT = """\
你是一位才华横溢的小说作家，能以不同风格创作短篇小说。
本项目会基于同一个脑洞生成 10 篇彼此明显不同的短篇小说；风格不限，由你自行决定。
请确保每一篇都有独立的题材/设定/叙事角度/文风选择，并避免重复同一套人物与世界观模板。
请以 JSON 格式返回，包含以下字段：
  - title: 小说标题（字符串）
  - content: 小说正文（字符串，至少 800 字）
  - writing_approach: 创作思路说明（字符串，说明选题角度、结构安排、风格把握等，100~200 字）
"""


def generate_novel(seed: str, style: NovelStyle, attempt: int = 1) -> Novel:
    """Ask the LLM to write one of the 10 novels based on *seed*.

    Parameters
    ----------
    seed:
        The initial story idea / brain-spark provided by the user.
    style:
        One of the five target novel styles.
    attempt:
        Generation attempt number (used for logging / model records).
    """
    slot_no = _SLOT_INDEX[style]
    user_prompt = (
        f"初始脑洞：{seed}\n\n"
        f"当前要生成：第 {slot_no} / 10 篇短篇小说（风格不限）。\n"
        "要求：\n"
        "1) 你自行选择题材、时空背景、叙事视角、文风与结构，使其与其他 9 篇尽量不同；\n"
        "2) 情节完整、人物立体、有明确冲突与转折；\n"
        "3) 正文至少 800 字；\n"
        f"4) {'这是重写版：上一版质量不达标，请在保留核心创意的同时大幅提升质量。' if attempt > 1 else '请直接创作。'}"
    )

    data = chat_json(_SYSTEM_PROMPT, user_prompt)

    return Novel(
        style=style,
        title=data.get("title", "无题"),
        content=data.get("content", ""),
        writing_approach=data.get("writing_approach", ""),
        attempt=attempt,
    )


def generate_all_novels(seed: str) -> list[Novel]:
    """Generate one novel for each of the ten styles.

    Returns a list of ten :class:`Novel` objects in the order defined by
    :class:`NovelStyle`.
    """
    return [generate_novel(seed, style) for style in NovelStyle]
