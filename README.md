# TaleSeed

[English](README.md) | [中文](README_CN.md)

Plant a seed of imagination, grow a novel. AI-powered story generation from a single spark of inspiration.

## Overview

TaleSeed takes an initial creative idea ("脑洞") and uses a large language model to automatically:

1. **Generate** ten short novels in ten distinctly different styles.
2. **Review** each novel with the LLM acting as a literary critic.
3. **Rewrite** any novel that fails the quality review (score < 6/10) — up to a configurable number of retries.
4. **Report** — produce a Markdown + JSON report covering novel name, content summary, writing style, and creative approach.

### Ten Novel Styles

| Style | Description |
|-------|-------------|
| 浪漫爱情 | Romantic love — delicate emotions, psychological depth |
| 科幻冒险 | Sci-fi adventure — grand world-building, fast-paced action |
| 悬疑推理 | Mystery/thriller — layered puzzles, unexpected twists |
| 奇幻魔法 | Fantasy/magic — imaginative world, unique magic systems |
| 历史武侠 | Historical martial arts — classical tone, chivalric spirit |
| 都市言情 | Urban romance — modern city life, realistic emotions |
| 玄幻修仙 | Xianxia/cultivation — cultivation systems, immortal world |
| 恐怖惊悚 | Horror/suspense — eerie atmosphere, psychological dread |
| 青春校园 | Youth/campus — coming-of-age, friendships, first love |
| 现实主义 | Realism — social reflection, authentic human experience |

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables (or place them in a `.env` file):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | — | API key for the LLM service |
| `OPENAI_BASE_URL` | ❌ | OpenAI | Base URL for OpenAI-compatible endpoints |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | Model name |
| `TALE_OUTPUT_DIR` | ❌ | `output/` | Directory for generated reports |
| `TALE_MAX_RETRIES` | ❌ | `3` | Maximum rewrites per novel on failed review |

## Usage

```bash
# Pass the seed directly on the command line
python main.py "一颗流星坠入古代江湖，引发了一场改变武林格局的争斗"

# Interactive mode (prompts for input)
python main.py

# Custom output directory and retry limit
python main.py "神秘的量子纠缠让两个平行世界开始交汇" \
    --output-dir ./my_output \
    --max-retries 5
```

The report is saved to `output/report.md` (Markdown) and `output/report.json` (JSON) by default.

### Report Contents

Each novel entry in the report includes:

- **小说名称** — Novel title
- **内容摘要** — Content summary (first paragraph excerpt)
- **编写风格** — Writing style
- **编写思路** — Creative approach and writing strategy
- **审核意见** — LLM review feedback and scores
- **创作尝试次数** — How many generation attempts were needed

## Project Structure

```
TaleSeed/
├── main.py              # Entry point / CLI
├── requirements.txt
├── src/
│   ├── models.py        # Data models (Novel, ReviewResult, Report)
│   ├── llm_client.py    # OpenAI-compatible LLM client wrapper
│   ├── generator.py     # Novel generation logic
│   ├── reviewer.py      # Novel review logic
│   ├── reporter.py      # Report serialisation
│   └── workflow.py      # End-to-end orchestration
└── tests/
    ├── test_models.py
    ├── test_generator.py
    ├── test_reviewer.py
    ├── test_reporter.py
    └── test_workflow.py
```

## Running Tests

```bash
pytest tests/ -v
```

