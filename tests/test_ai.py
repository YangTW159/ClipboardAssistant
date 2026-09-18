"""Tests for core.ai_assistant: prompt payload building and config validation."""
import pytest

from core.ai_assistant import AI_PROMPTS, build_payload, call_ai


def test_build_payload_structure():
    payload = build_payload("deepseek-chat", "总结", "hello world")
    assert payload["model"] == "deepseek-chat"
    assert payload["stream"] is False
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][1]["content"] == "hello world"


def test_all_actions_have_prompts():
    for action in ("总结", "翻译", "润色"):
        assert action in AI_PROMPTS


def test_unknown_action_falls_back_to_summary():
    payload = build_payload("m", "不存在的动作", "x")
    assert payload["messages"][0]["content"] == AI_PROMPTS["总结"]


def test_missing_api_key_raises():
    with pytest.raises(ValueError, match="API Key"):
        call_ai("https://api.example.com", "", "model", "总结", "text")


def test_missing_endpoint_raises():
    with pytest.raises(ValueError):
        call_ai("", "sk-xxx", "model", "总结", "text")
