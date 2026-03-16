# TaleSeed

[English](README.md) | [中文](README_CN.md)

播下一粒想象的种子，收获一部小说。基于 AI 的故事生成工具，从一个灵感火花出发，自动创作短篇小说。

## 项目简介

TaleSeed 接收一个初始创意（"脑洞"），并使用大语言模型自动完成以下流程：

1. **生成** — 围绕同一个脑洞，生成 10 篇彼此明显不同的短篇小说（风格不限）。
2. **审核** — 让 LLM 担任文学评论家，对每篇小说进行评分。
3. **重写** — 对审核不通过（评分 < 6/10）的小说进行重写，最多重试可配置次数。
4. **报告** — 生成包含小说名称、内容摘要、编写风格、创作思路的 Markdown + JSON 报告。

## 安装

```bash
pip install -r requirements.txt
```

## 配置

设置以下环境变量（或写入 `.env` 文件）：

| 变量名 | 是否必填 | 默认值 | 说明 |
|--------|----------|--------|------|
| `TALE_LLM_PROVIDER` | ❌ | `openai` | LLM 服务商：`openai` / `deepseek` / `qwen` / `kimi` / `grok` / `minmax` |
| `TALE_LLM_API_KEY` | ❌ | — | API Key（优先级高于 `*_API_KEY`） |
| `TALE_LLM_BASE_URL` | ❌ | — | OpenAI 兼容接口地址（优先级高于 `*_BASE_URL`） |
| `TALE_LLM_MODEL` | ❌ | — | 模型名称（优先级高于 `*_MODEL`） |
| `TALE_OUTPUT_DIR` | ❌ | `output/` | 报告输出目录 |
| `TALE_MAX_RETRIES` | ❌ | `3` | 每篇小说审核失败后的最大重写次数 |

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
