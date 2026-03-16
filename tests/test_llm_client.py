"""Tests for the llm_client provider selection and env resolution."""

from __future__ import annotations

import pytest

from src.llm_client import LLMConfigurationError, get_settings


_ENV_KEYS = [
    # Provider selector + provider-agnostic overrides
    "TALE_LLM_PROVIDER",
    "TALE_LLM_API_KEY",
    "TALE_LLM_BASE_URL",
    "TALE_LLM_MODEL",
    # Legacy OpenAI names
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    # Provider-specific names
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MODEL",
]


def _clear_env(monkeypatch):
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_default_provider_uses_openai_legacy_env(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    settings = get_settings(strict=True)

    assert settings.provider == "openai"
    assert settings.api_key == "sk-test"
    assert settings.base_url is None
    assert settings.model == "gpt-4o-mini"


def test_deepseek_provider_reads_provider_specific_env(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TALE_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-test")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")

    settings = get_settings(strict=True)

    assert settings.provider == "deepseek"
    assert settings.api_key == "ds-test"
    assert settings.base_url == "https://example.invalid/v1"
    assert settings.model == "deepseek-chat"


def test_provider_agnostic_overrides_take_precedence(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TALE_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-test")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")

    monkeypatch.setenv("TALE_LLM_API_KEY", "override-key")
    monkeypatch.setenv("TALE_LLM_BASE_URL", "https://override.invalid/v1")
    monkeypatch.setenv("TALE_LLM_MODEL", "override-model")

    settings = get_settings(strict=True)

    assert settings.api_key == "override-key"
    assert settings.base_url == "https://override.invalid/v1"
    assert settings.model == "override-model"


def test_non_openai_provider_requires_base_url_and_model_in_strict_mode(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TALE_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-test")

    with pytest.raises(LLMConfigurationError):
        get_settings(strict=True)


def test_unsupported_provider_raises_in_strict_mode(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TALE_LLM_PROVIDER", "unknown")

    with pytest.raises(LLMConfigurationError):
        get_settings(strict=True)
