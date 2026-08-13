import json
import os
import sys
from pathlib import Path


APP_NAME = "ClipboardAssistant"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
DEFAULTS = {
    "auto_start": False,
    "show_window_on_start": True,
    "max_records": 1000,
    "duplicate_window_seconds": 3,
    "icon_path": "",
}


def application_directory() -> Path:
    directory = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / APP_NAME
    directory.mkdir(parents=True, exist_ok=True)
    return directory


SETTINGS_FILE = application_directory() / "settings.json"


def load_settings() -> dict:
    try:
        saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        saved = {}
    return DEFAULTS | {key: saved[key] for key in DEFAULTS if key in saved}


def save_settings(settings: dict):
    SETTINGS_FILE.write_text(
        json.dumps(DEFAULTS | settings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _update_auto_start(bool(settings.get("auto_start")))


def application_command() -> str:
    executable = Path(sys.executable if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent / "main.py")
    if getattr(sys, "frozen", False):
        return f'"{executable}"'
    return f'"{sys.executable}" "{executable}"'


def _update_auto_start(enabled: bool):
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, application_command())
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
    except OSError as error:
        raise RuntimeError(f"无法更新开机启动设置：{error}") from error
