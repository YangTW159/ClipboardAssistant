# Clipboard Assistant

A lightweight Windows clipboard history manager built with **Python + PyQt6**.
It runs quietly in the system tray, records every copied text snippet locally,
and lets you search, re-copy, delete, export, or process it with AI — no cloud,
no telemetry.

中文说明请参阅 [项目说明.md](项目说明.md)。

[![CI](https://github.com/YangTW159/ClipboardAssistant/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/YangTW159/ClipboardAssistant/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/YangTW159/ClipboardAssistant?label=download&color=success)](https://github.com/YangTW159/ClipboardAssistant/releases/latest)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Features

- **Real-time monitoring** — automatically records text copied from any application.
- **System tray resident** — closing the window minimizes to the tray; right-click to fully quit.
- **Instant search** — filter history by keyword as you type.
- **One-click re-copy** — double-click any entry to put it back on the clipboard.
- **Single-record delete & clear-all** — right-click to remove an entry, or wipe history at once.
- **Smart dedup** — suppresses duplicate copies within a configurable time window.
- **Capacity limit** — keep only the newest *N* records (default 1000).
- **Export to TXT** — dump your whole history to a text file.
- **One-click AI actions** — right-click any entry to **summarize / translate / polish** it via an OpenAI-compatible API (DeepSeek, Volcengine Ark, etc.); calls run on a background thread so the UI never freezes.
- **Autostart & customization** — launch on boot, show window on start, custom tray icon.
- **Single-instance guard** — prevents duplicate listeners via a local socket.
- **100% local & private** — history lives in a local SQLite database; nothing is uploaded.

## Screenshot

![Clipboard Assistant main window](assets/main-window.png)

## Quick start

### Option A — Download the executable (no Python needed)

1. Go to the [Releases page](https://github.com/YangTW159/ClipboardAssistant/releases/latest).
2. Download `ClipboardAssistant.exe` from the latest release.
3. Run it. The app appears in the system tray.

> Windows SmartScreen may warn on first run (unsigned `.exe`). Choose
> **More info → Run anyway**.

### Option B — Run from source

Requirements: Windows 10+, Python 3.11+.

```powershell
git clone https://github.com/YangTW159/ClipboardAssistant.git
cd ClipboardAssistant
python -m pip install -r requirements.txt
python main.py
```

Close the window to send the app to the tray; use the tray menu to reopen or quit.

## AI actions

Right-click a history entry and choose **AI 总结 / 翻译 / 润色**. The result
shows in a dialog with a "copy to clipboard" button.

To enable it, open **Settings** and fill in:

| Field | Example |
| --- | --- |
| AI 接口地址 (base URL) | `https://api.deepseek.com` |
| AI API Key | `sk-...` |
| 模型名称 (model) | `deepseek-chat` |

Any OpenAI-compatible endpoint works (DeepSeek, Volcengine Ark/Doubao,
Moonshot, OpenAI, …). Your API key is stored only in the local settings file.

## Build a standalone EXE

```powershell
python -m pip install pyinstaller pillow
python -m PyInstaller --noconfirm --clean --onefile --windowed `
  --name "ClipboardAssistant" --icon "1.ico" --add-data "1.ico;." main.py
```

The executable is produced in `dist/`.

## Development

Install dev dependencies and run the tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover the database layer (insert / dedup / capacity / delete / export),
the settings layer (defaults / save-load round-trip / malformed JSON), and the
AI request builder (payload structure / config validation). They use temporary
directories, so they never touch your real clipboard database.

### Continuous integration

- **[CI](.github/workflows/ci.yml)** runs the test suite on every push and pull
  request, on Windows with Python 3.11 and 3.12.
- **[Release](.github/workflows/release.yml)** builds the standalone EXE with
  PyInstaller and attaches it to a GitHub Release whenever a `v*` tag is pushed.

### Cutting a new release

```powershell
git tag v1.1.0
git push origin v1.1.0
```

This triggers the release workflow, which builds `ClipboardAssistant.exe` and
creates a GitHub Release with auto-generated notes.

## Data & privacy

History and settings are stored locally under:

```text
%LOCALAPPDATA%\ClipboardAssistant\
```

The app only records **text** clipboard content. Because that history may contain
passwords, tokens, or private messages, the local database and settings file are
excluded via `.gitignore` and are never committed. When you use an AI action,
only the selected text is sent to the provider you configured; the app itself
uploads nothing.

Avoid copying secrets; if you do, delete the entry in the app or use "clear all".

## Project structure

```text
core/   clipboard listener, settings, AI assistant + background worker
db/     SQLite history storage
ui/     main window, settings dialog, tray icon, AI result dialog
tests/  pytest unit tests
main.py application entry point
```

## License

[MIT](LICENSE) © YangTW159
