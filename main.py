#!/usr/bin/env python3
"""TaleSeed – AI-powered novel generator entry point.

Usage
-----
    python main.py "一颗流星坠入古代江湖，引发了一场改变武林格局的争斗"

Environment variables
---------------------
    TALE_LLM_PROVIDER – optional (openai/deepseek/qwen/kimi/grok/minmax; default: openai)
    TALE_LLM_API_KEY  – optional (overrides provider-specific *_API_KEY)
    TALE_LLM_BASE_URL – optional (overrides provider-specific *_BASE_URL)
    TALE_LLM_MODEL    – optional (overrides provider-specific *_MODEL)

    Legacy / compatibility for provider=openai:
    OPENAI_API_KEY   – required when using OpenAI
    OPENAI_BASE_URL  – optional (for OpenAI-compatible third-party endpoints)
    OPENAI_MODEL     – optional (defaults to gpt-4o-mini)
    TALE_OUTPUT_DIR  – optional output directory (defaults to ./output)
    TALE_MAX_RETRIES – optional max rewrite attempts per novel (defaults to 3)
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

from dotenv import load_dotenv


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taleseed",
        description="Plant a seed of imagination, grow five novels.",
    )
    parser.add_argument(
        "seed",
        nargs="?",
        default=None,
        help="Initial story idea / brain-spark (if omitted, read from stdin)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("TALE_OUTPUT_DIR", "output"),
        help="Directory to write the report files (default: output/)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=int(os.environ.get("TALE_MAX_RETRIES", "3")),
        help="Maximum rewrite attempts per novel when review fails (default: 3)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: WARNING)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()

    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    )

    from src.llm_client import LLMConfigurationError, get_settings

    try:
        # Validate early so we can fail fast with a clear error message.
        get_settings(strict=True)
    except LLMConfigurationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    seed: str = args.seed or ""
    if not seed:
        if sys.stdin.isatty():
            print("请输入初始脑洞（按 Enter 确认）：", end=" ", flush=True)
        seed = sys.stdin.readline().strip()

    if not seed:
        print("Error: A story seed is required.", file=sys.stderr)
        return 1

    from src.workflow import run

    run(
        seed,
        max_retries=args.max_retries,
        output_dir=args.output_dir,
        verbose=not args.quiet,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
