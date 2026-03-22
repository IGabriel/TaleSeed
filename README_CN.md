# TaleSeed

[English](README.md) | [中文](README_CN.md)

播下一粒想象的种子，收获一部小说。基于 AI 的故事生成工具，从一个灵感火花出发，自动创作短篇小说。

## 项目简介

TaleSeed 接收一个初始创意（"脑洞"），并使用大语言模型自动完成以下流程：

1. **策划** — 对每一篇小说依次敲定：写作手法、主要角色、章节大纲，并逐步评估与修正。
2. **创作** — 按大纲分章写作，每篇目标约 1 万字（不足会自动补写至至少约 9000 字）。
3. **审核** — 让 LLM 担任文学评论家，对每篇小说进行评分。
4. **重写** — 审核不通过时，保留既定的写作手法/角色/大纲，仅重写正文（最多重试可配置次数）。
5. **报告** — 生成总报告（Markdown + JSON），并将每篇小说保存为独立的 `.md` 文件。

## 安装

```bash
pip install -r requirements.txt
```

## 配置

本仓库提供了可直接复制的环境变量模板文件（见 `env_templates/`）。推荐先选择一个模板复制为 `.env`，再填入 API Key 等信息：

```bash
# 例如：使用阿里云百炼（DashScope）调用千问
cp env_templates/qwen_bailian.env_template .env

# 或：使用 OpenAI
# cp env_templates/openai.env_template .env

# 然后编辑 .env，填入 API Key / Base URL / Model
```

你也可以直接设置以下环境变量（或写入 `.env` 文件）：

| 变量名 | 是否必填 | 默认值 | 说明 |
|--------|----------|--------|------|
| `TALE_LLM_PROVIDER` | ❌ | `openai` | LLM 服务商：`openai` / `deepseek` / `qwen` / `kimi` / `grok` / `minmax` |
| `TALE_LLM_API_KEY` | ❌ | — | API Key（优先级高于 `*_API_KEY`） |
| `TALE_LLM_BASE_URL` | ❌ | — | OpenAI 兼容接口地址（优先级高于 `*_BASE_URL`） |
| `TALE_LLM_MODEL` | ❌ | — | 模型名称（优先级高于 `*_MODEL`） |
| `TALE_OUTPUT_DIR` | ❌ | `output/` | 报告输出目录 |
| `TALE_MAX_RETRIES` | ❌ | `3` | 每篇小说审核失败后的最大重写次数 |

说明：
- `TALE_MAX_RETRIES` 会同时影响策划阶段（写作手法/角色/大纲）的最多尝试次数，以及正文审核失败后的最多重写次数。

不同服务商对应的环境变量
------------------------
当设置了 `TALE_LLM_PROVIDER` 后，TaleSeed 会按如下规则读取环境变量：

- `openai`：`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`
- `deepseek`：`DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`
- `qwen`：`QWEN_API_KEY`、`QWEN_BASE_URL`、`QWEN_MODEL`
- `kimi`：`KIMI_API_KEY`、`KIMI_BASE_URL`、`KIMI_MODEL`
- `grok`：`GROK_API_KEY`、`GROK_BASE_URL`、`GROK_MODEL`
- `minmax`：`MINMAX_API_KEY`、`MINMAX_BASE_URL`、`MINMAX_MODEL`

说明：
- 当 `provider=openai` 时，`OPENAI_BASE_URL` 可不填。
- 对于非 OpenAI 的服务商，一般需要同时设置 `*_BASE_URL` 和 `*_MODEL`，具体取值请以对应服务商的 OpenAI 兼容接口文档为准。

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

输出文件默认保存在 `output/`：

- `output/report.md`：总报告（Markdown）
- `output/report.json`：总报告（JSON）
- `output/novel_01.md` ~ `output/novel_10.md`：每篇小说独立 Markdown 文件

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
