import os
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from core.settings import application_directory, load_settings


APP_NAME = "ClipboardAssistant"
DB_FILE = application_directory() / "clipboard.db"
LEGACY_DB_FILE = Path(__file__).resolve().parent.parent / "clipboard.db"


def _connect():
    return sqlite3.connect(DB_FILE, timeout=5)


def _migrate_legacy_database():
    if not DB_FILE.exists() and LEGACY_DB_FILE.exists() and LEGACY_DB_FILE != DB_FILE:
        shutil.copy2(LEGACY_DB_FILE, DB_FILE)


def init_db():
    _migrate_legacy_database()
    with closing(_connect()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clipboard_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                create_time TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_record(content: str) -> tuple[int, str] | None:
    if not content.strip():
        return None
    now = datetime.now()
    create_time = now.strftime("%Y-%m-%d %H:%M:%S")
    settings = load_settings()
    with closing(_connect()) as conn:
        latest = conn.execute(
            "SELECT content, create_time FROM clipboard_history ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if latest and latest[0] == content:
            latest_time = datetime.strptime(latest[1], "%Y-%m-%d %H:%M:%S")
            if (now - latest_time).total_seconds() < settings["duplicate_window_seconds"]:
                return None
        cursor = conn.execute(
            "INSERT INTO clipboard_history (content, create_time) VALUES (?, ?)",
            (content, create_time),
        )
        conn.execute(
            """
            DELETE FROM clipboard_history
            WHERE id NOT IN (
                SELECT id FROM clipboard_history ORDER BY id DESC LIMIT ?
            )
            """,
            (settings["max_records"],),
        )
        conn.commit()
        return cursor.lastrowid, create_time


def get_all_records(search_text: str = "") -> list[tuple[int, str, str]]:
    query = "SELECT id, content, create_time FROM clipboard_history"
    params = []
    if search_text:
        query += " WHERE content LIKE ?"
        params.append(f"%{search_text}%")
    query += " ORDER BY id DESC"
    with closing(_connect()) as conn:
        return conn.execute(query, params).fetchall()


def delete_record(record_id: int):
    with closing(_connect()) as conn:
        conn.execute("DELETE FROM clipboard_history WHERE id = ?", (record_id,))
        conn.commit()


def clear_all_records():
    with closing(_connect()) as conn:
        conn.execute("DELETE FROM clipboard_history")
        conn.commit()


def export_to_txt(save_path: str):
    with open(save_path, "w", encoding="utf-8") as file:
        for _, content, created_at in get_all_records():
            file.write(f"[{created_at}]\n{content}\n{'-' * 50}\n")
