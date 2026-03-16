"""LLM client wrapper for TaleSeed.

This project talks to LLM services through the OpenAI Python SDK because many
providers expose an OpenAI-compatible API surface.

Provider selection
------------------
Set ``TALE_LLM_PROVIDER`` to choose which provider-specific environment
variables are used:

- ``openai``   -> ``OPENAI_API_KEY``, ``OPENAI_BASE_URL``, ``OPENAI_MODEL``
- ``deepseek`` -> ``DEEPSEEK_API_KEY``, ``DEEPSEEK_BASE_URL``, ``DEEPSEEK_MODEL``
- ``qwen``     -> ``QWEN_API_KEY``, ``QWEN_BASE_URL``, ``QWEN_MODEL``
- ``kimi``     -> ``KIMI_API_KEY``, ``KIMI_BASE_URL``, ``KIMI_MODEL``
- ``grok``     -> ``GROK_API_KEY``, ``GROK_BASE_URL``, ``GROK_MODEL``
- ``minmax``   -> ``MINMAX_API_KEY``, ``MINMAX_BASE_URL``, ``MINMAX_MODEL``

You can also use the provider-agnostic overrides:
``TALE_LLM_API_KEY``, ``TALE_LLM_BASE_URL``, ``TALE_LLM_MODEL``.

Backwards compatibility: if ``TALE_LLM_PROVIDER`` is not set, we default to
``openai`` and keep using ``OPENAI_*``.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


class LLMConfigurationError(ValueError):
    """Raised when required LLM configuration is missing or invalid."""


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    api_key: str
    base_url: str | None
    model: str


_SUPPORTED_PROVIDERS: tuple[str, ...] = (
    "openai",
    "deepseek",
    "qwen",
    "kimi",
    "grok",
    "minmax",
)


def _normalize_provider(value: str | None) -> str:
    provider = (value or "openai").strip().lower()
    if not provider:
        return "openai"
    return provider


def _env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def get_settings(*, strict: bool = False) -> LLMSettings:
    """Resolve provider/model/credentials from environment variables.

    If *strict* is True, missing required settings raises
    :class:`LLMConfigurationError`.
    """

    provider = _normalize_provider(_env("TALE_LLM_PROVIDER"))
    if provider not in _SUPPORTED_PROVIDERS:
        if strict:
            raise LLMConfigurationError(
                f"Unsupported TALE_LLM_PROVIDER={provider!r}. "
                f"Supported: {', '.join(_SUPPORTED_PROVIDERS)}"
            )
        provider = "openai"

    prefix = provider.upper()

    api_key = _env("TALE_LLM_API_KEY") or _env(f"{prefix}_API_KEY")
    base_url = _env("TALE_LLM_BASE_URL") or _env(f"{prefix}_BASE_URL")
    model = _env("TALE_LLM_MODEL") or _env(f"{prefix}_MODEL")

    # Legacy OpenAI names (default path)
    if provider == "openai":
        api_key = api_key or _env("OPENAI_API_KEY")
        base_url = base_url or _env("OPENAI_BASE_URL")
        model = model or _env("OPENAI_MODEL")

    if provider == "openai":
        model = model or "gpt-4o-mini"

    if strict:
        if not api_key:
            raise LLMConfigurationError(
                "Missing API key. Set TALE_LLM_API_KEY, or set "
                f"{prefix}_API_KEY (or OPENAI_API_KEY for provider=openai)."
            )

        # For non-OpenAI providers we cannot guess the endpoint/model safely.
        if provider != "openai" and not base_url:
            raise LLMConfigurationError(
                f"Missing base URL for provider={provider!r}. "
                f"Set TALE_LLM_BASE_URL or {prefix}_BASE_URL."
            )
        if provider != "openai" and not model:
            raise LLMConfigurationError(
                f"Missing model for provider={provider!r}. "
                f"Set TALE_LLM_MODEL or {prefix}_MODEL."
            )

    return LLMSettings(
        provider=provider,
        api_key=api_key or "",
        base_url=base_url,
        model=model or "gpt-4o-mini",
    )


def _get_client(settings: LLMSettings) -> OpenAI:
    """Build an OpenAI-compatible client from resolved settings."""
    kwargs: dict[str, Any] = {"api_key": settings.api_key}
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    return OpenAI(**kwargs)


def get_model() -> str:
    """Return the resolved model name."""
    return get_settings().model


def chat(system: str, user: str, *, temperature: float = 0.8) -> str:
    """Send a chat completion request and return the response text."""
    settings = get_settings(strict=True)
    client = _get_client(settings)
    response = client.chat.completions.create(
        model=settings.model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def chat_json(system: str, user: str, *, temperature: float = 0.2) -> dict:
    """Send a chat completion request and parse the JSON response."""
    settings = get_settings(strict=True)
    client = _get_client(settings)
    response = client.chat.completions.create(
        model=settings.model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    return json.loads(raw)
