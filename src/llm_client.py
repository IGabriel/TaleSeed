"""LLM client wrapper for TaleSeed."""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI


def _get_client() -> OpenAI:
    """Build an OpenAI-compatible client from environment variables.

    Supported environment variables:
      OPENAI_API_KEY   – required
      OPENAI_BASE_URL  – optional (for third-party OpenAI-compatible endpoints)
      OPENAI_MODEL     – optional (defaults to gpt-4o-mini)
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL")
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def get_model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def chat(system: str, user: str, *, temperature: float = 0.8) -> str:
    """Send a chat completion request and return the response text."""
    client = _get_client()
    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def chat_json(system: str, user: str, *, temperature: float = 0.2) -> dict:
    """Send a chat completion request and parse the JSON response."""
    client = _get_client()
    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    return json.loads(raw)
