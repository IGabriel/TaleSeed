# TaleSeed

[English](README.md) | [中文](README_CN.md)

播下一粒想象的种子，收获一部小说。基于 AI 的故事生成工具，从一个灵感火花出发，自动创作短篇小说。

## 项目简介

TaleSeed 接收一个初始创意（"脑洞"），并使用大语言模型自动完成以下流程：

1. **生成** — 以十种截然不同的风格各创作一篇短篇小说。
2. **审核** — 让 LLM 担任文学评论家，对每篇小说进行评分。
3. **重写** — 对审核不通过（评分 < 6/10）的小说进行重写，最多重试可配置次数。
4. **报告** — 生成包含小说名称、内容摘要、编写风格、创作思路的 Markdown + JSON 报告。

### 十种小说风格

| 风格 | 说明 |
|------|------|
| 浪漫爱情 | 细腻情感描写、心理刻画，聚焦人物情感纠葛与成长 |
| 科幻冒险 | 宏大世界观设定、科技感十足，充满星际或未来冒险 |
| 悬疑推理 | 层层递进的谜题、反转迭出，结局出乎意料但逻辑严密 |
| 奇幻魔法 | 天马行空的世界构建、独特魔法体系，东西方奇幻色彩 |
| 历史武侠 | 融合真实历史背景、江湖侠义精神，文字古朴凝练 |
| 都市言情 | 现代都市生活为背景，情感真实细腻，贴近当代读者 |
| 玄幻修仙 | 宏大修炼体系与仙侠世界，主角历经磨难不断突破 |
| 恐怖惊悚 | 压抑诡异的氛围，心理恐惧与未知威胁，令人心悸 |
| 青春校园 | 校园生活为舞台，描绘青春懵懂情感、友情与成长 |
| 现实主义 | 深刻反映社会现实与人性百态，人文关怀与时代感并重 |

## 安装

```bash
pip install -r requirements.txt
```

## 配置

设置以下环境变量（或写入 `.env` 文件）：

| 变量名 | 是否必填 | 默认值 | 说明 |
|--------|----------|--------|------|
| `OPENAI_API_KEY` | ✅ | — | LLM 服务的 API 密钥 |
| `OPENAI_BASE_URL` | ❌ | OpenAI 官方地址 | 兼容 OpenAI 接口的自定义地址 |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | 模型名称 |
| `TALE_OUTPUT_DIR` | ❌ | `output/` | 报告输出目录 |
| `TALE_MAX_RETRIES` | ❌ | `3` | 每篇小说审核失败后的最大重写次数 |

## 使用方法

```bash
# 直接在命令行传入脑洞
python main.py "一颗流星坠入古代江湖，引发了一场改变武林格局的争斗"

# 交互模式（提示用户输入）
python main.py

# 自定义输出目录与重试次数
python main.py "神秘的量子纠缠让两个平行世界开始交汇" \
    --output-dir ./my_output \
    --max-retries 5
```

报告默认保存为 `output/report.md`（Markdown）和 `output/report.json`（JSON）。

### 报告内容

每篇小说的报告条目包含：

- **小说名称** — 小说标题
- **内容摘要** — 正文摘要（首段节选）
- **编写风格** — 所属创作风格
- **编写思路** — 创作角度、结构安排与风格把握
- **审核意见** — LLM 评审意见与各维度评分
- **创作尝试次数** — 生成所需的总尝试次数

## 项目结构

```
TaleSeed/
├── main.py              # 入口 / 命令行界面
├── requirements.txt
├── src/
│   ├── models.py        # 数据模型（Novel、ReviewResult、Report）
│   ├── llm_client.py    # OpenAI 兼容 LLM 客户端封装
│   ├── generator.py     # 小说生成逻辑
│   ├── reviewer.py      # 小说审核逻辑
│   ├── reporter.py      # 报告序列化
│   └── workflow.py      # 端到端编排流程
└── tests/
    ├── test_models.py
    ├── test_generator.py
    ├── test_reviewer.py
    ├── test_reporter.py
    └── test_workflow.py
```

## 运行测试

```bash
pytest tests/ -v
```
