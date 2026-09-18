"""Tests for core.settings: load/save, defaults merging, invalid files."""
import json

import pytest

import core.settings as settings_module


@pytest.fixture
def isolated_settings(tmp_path, monkeypatch):
    """Redirect settings.json to a temp file and disable registry touches."""
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_module, "SETTINGS_FILE", settings_file)
    # Never touch the Windows Run key during tests.
    monkeypatch.setattr(settings_module, "_update_auto_start", lambda enabled: None)
    return settings_file


def test_load_returns_defaults_when_missing(isolated_settings):
    cfg = settings_module.load_settings()
    assert cfg == settings_module.DEFAULTS


def test_save_then_load_roundtrip(isolated_settings):
    settings_module.save_settings({
        "auto_start": True,
        "show_window_on_start": False,
        "max_records": 500,
        "duplicate_window_seconds": 10,
        "icon_path": "",
    })
    cfg = settings_module.load_settings()
    assert cfg["auto_start"] is True
    assert cfg["show_window_on_start"] is False
    assert cfg["max_records"] == 500
    assert cfg["duplicate_window_seconds"] == 10


def test_unknown_keys_are_ignored(isolated_settings):
    isolated_settings.write_text(
        json.dumps({"max_records": 123, "totally_unknown": "x"}),
        encoding="utf-8",
    )
    cfg = settings_module.load_settings()
    assert cfg["max_records"] == 123
    assert "totally_unknown" not in cfg


def test_malformed_json_falls_back_to_defaults(isolated_settings):
    isolated_settings.write_text("{ not valid json", encoding="utf-8")
    cfg = settings_module.load_settings()
    assert cfg == settings_module.DEFAULTS
