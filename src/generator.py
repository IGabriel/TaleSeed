"""Novel generation logic for TaleSeed."""

from __future__ import annotations

from src.llm_client import chat_json
from src.models import Novel, NovelStyle

_STYLE_GUIDANCE: dict[NovelStyle, str] = {
    NovelStyle.ROMANCE: (
        "浪漫爱情风格：细腻的情感描写、心理刻画、优美的文笔，聚焦人物之间的情感纠葛与成长。"
    ),
    NovelStyle.SCIFI: (
        "科幻冒险风格：宏大的世界观设定、科技感十足、节奏紧凑，充满惊险刺激的星际或未来冒险。"
    ),
    NovelStyle.MYSTERY: (
        "悬疑推理风格：层层递进的谜题、反转迭出的情节、紧张的氛围，结局出乎意料但逻辑严密。"
    ),
    NovelStyle.FANTASY: (
        "奇幻魔法风格：天马行空的世界构建、魔法体系独特、人物命运跌宕起伏，充满东方或西方奇幻色彩。"
    ),
    NovelStyle.HISTORICAL: (
        "历史武侠风格：融合真实历史背景、江湖恩怨情仇、侠义精神，文字古朴凝练，人物形象鲜明。"
    ),
    NovelStyle.URBAN: (
        "都市言情风格：聚焦现代都市生活，情感细腻真实，描绘职场、家庭与爱情的多重交织，贴近当代读者的生活体验。"
    ),
    NovelStyle.XIANXIA: (
        "玄幻修仙风格：构建宏大的修炼体系与仙侠世界，主角历经磨难不断突破，境界升华与家国情怀并重，充满东方神话色彩。"
    ),
    NovelStyle.HORROR: (
        "恐怖惊悚风格：营造压抑诡异的氛围，以心理恐惧与未知威胁推动情节，结局出人意料，令读者心悸难安。"
    ),
    NovelStyle.CAMPUS: (
        "青春校园风格：以校园生活为舞台，描绘青春期的懵懂情感、友情羁绊与成长蜕变，语言清新活泼，充满青春气息。"
    ),
    NovelStyle.REALISM: (
        "现实主义风格：深刻反映社会现实与人性百态，人物塑造立体丰满，情节源于生活而高于生活，具有强烈的时代感与人文关怀。"
    ),
}

_SYSTEM_PROMPT = """\
你是一位才华横溢的小说作家，能以不同风格创作短篇小说。
请严格按照指定风格创作，确保风格鲜明、情节完整、人物立体。
请以 JSON 格式返回，包含以下字段：
  - title: 小说标题（字符串）
  - content: 小说正文（字符串，至少 800 字）
  - writing_approach: 创作思路说明（字符串，说明选题角度、结构安排、风格把握等，100~200 字）
"""


def generate_novel(seed: str, style: NovelStyle, attempt: int = 1) -> Novel:
    """Ask the LLM to write a novel for *style* based on *seed*.

    Parameters
    ----------
    seed:
        The initial story idea / brain-spark provided by the user.
    style:
        One of the five target novel styles.
    attempt:
        Generation attempt number (used for logging / model records).
    """
    style_guidance = _STYLE_GUIDANCE[style]
    user_prompt = (
        f"初始脑洞：{seed}\n\n"
        f"创作风格要求：{style_guidance}\n\n"
        f"请基于以上脑洞，创作一篇{'重写版（第 ' + str(attempt) + ' 次尝试，上一版质量不达标，请在保留核心创意的同时大幅提升质量）' if attempt > 1 else ''}该风格的短篇小说。"
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
