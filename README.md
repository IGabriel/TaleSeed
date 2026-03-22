# TaleSeed

[English](README.md) | [中文](README_CN.md)

Plant a seed of imagination, grow a novel. AI-powered story generation from a single spark of inspiration.

## Overview

TaleSeed takes an initial creative idea ("脑洞") and uses a large language model to automatically:

1. **Plan** each novel: decide writing technique, main characters, and a chapter outline, with evaluation and retries.
2. **Draft** a long-form novel following the outline (target ~10k Chinese characters; auto-extends to at least ~9k).
3. **Review** each novel with the LLM acting as a literary critic.
4. **Rewrite** drafts that fail review (the plan is kept; only the draft is rewritten) — up to a configurable number of retries.
5. **Report** — produce a Markdown + JSON report and also save each novel as an individual `.md` file.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

This repo includes copy-ready env templates (see `env_templates/`). Recommended flow: copy one template to `.env`, then fill in your API key / base URL / model:

```bash
# Example: use Alibaba Cloud Bailian (DashScope) via the OpenAI-compatible endpoint
cp env_templates/qwen_bailian.env_template .env

# Or: use OpenAI
# cp env_templates/openai.env_template .env

# Then edit .env and fill your secrets
```

You can also set the following environment variables (or place them in a `.env` file):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TALE_LLM_PROVIDER` | ❌ | `openai` | LLM provider: `openai` / `deepseek` / `qwen` / `kimi` / `grok` / `minmax` |
| `TALE_LLM_API_KEY` | ❌ | — | Provider API key (overrides `*_API_KEY`) |
| `TALE_LLM_BASE_URL` | ❌ | — | OpenAI-compatible base URL (overrides `*_BASE_URL`) |
| `TALE_LLM_MODEL` | ❌ | — | Model name (overrides `*_MODEL`) |
| `TALE_OUTPUT_DIR` | ❌ | `output/` | Directory for generated reports |
| `TALE_MAX_RETRIES` | ❌ | `3` | Maximum rewrites per novel on failed review |

Notes:
- `TALE_MAX_RETRIES` is used as the upper bound for both (a) planning retries (technique/characters/outline) and (b) draft rewrites after a failed review.

Provider-specific variables
--------------------------
When `TALE_LLM_PROVIDER` is set, TaleSeed will look for these variables:

- `openai`: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`
- `deepseek`: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`
- `qwen`: `QWEN_API_KEY`, `QWEN_BASE_URL`, `QWEN_MODEL`
- `kimi`: `KIMI_API_KEY`, `KIMI_BASE_URL`, `KIMI_MODEL`
- `grok`: `GROK_API_KEY`, `GROK_BASE_URL`, `GROK_MODEL`
- `minmax`: `MINMAX_API_KEY`, `MINMAX_BASE_URL`, `MINMAX_MODEL`

Notes:
- For `provider=openai`, `OPENAI_BASE_URL` is optional.
- For non-OpenAI providers, you typically need to set both `*_BASE_URL` and
    `*_MODEL` according to your provider's OpenAI-compatible API.

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

Outputs are saved under `output/` by default:

- `output/report.md` (Markdown report)
- `output/report.json` (JSON report)
- `output/novel_01.md` ~ `output/novel_10.md` (one Markdown file per novel)

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

