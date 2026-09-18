"""Tests for db.database: insert/dedup/cap/delete/clear/export."""
import pytest

import db.database as db


@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    """Point the module-level DB_FILE at an isolated temp database."""
    db_file = tmp_path / "test_clipboard.db"
    monkeypatch.setattr(db, "DB_FILE", db_file)
    db.init_db()
    return db_file


@pytest.fixture
def settings_cap(monkeypatch):
    """Override the settings used by insert_record with controlled values."""
    def _apply(max_records=1000, duplicate_window_seconds=3):
        monkeypatch.setattr(db, "load_settings", lambda: {
            "max_records": max_records,
            "duplicate_window_seconds": duplicate_window_seconds,
        })
    return _apply


def test_insert_and_fetch(fresh_db, settings_cap):
    settings_cap()
    assert db.insert_record("hello world") is not None
    rows = db.get_all_records()
    assert len(rows) == 1
    assert rows[0][1] == "hello world"


def test_blank_content_is_rejected(fresh_db, settings_cap):
    settings_cap()
    assert db.insert_record("   ") is None
    assert db.get_all_records() == []


def test_duplicate_suppressed_within_window(fresh_db, settings_cap):
    settings_cap(duplicate_window_seconds=3600)
    assert db.insert_record("same text") is not None
    # Second identical copy inside the dedup window is dropped.
    assert db.insert_record("same text") is None
    assert len(db.get_all_records()) == 1


def test_duplicate_allowed_when_window_closed(fresh_db, settings_cap):
    settings_cap(duplicate_window_seconds=0)
    assert db.insert_record("same text") is not None
    assert db.insert_record("same text") is not None
    assert len(db.get_all_records()) == 2


def test_max_records_enforced(fresh_db, settings_cap):
    settings_cap(max_records=3, duplicate_window_seconds=0)
    for i in range(5):
        db.insert_record(f"item {i}")
    rows = db.get_all_records()
    assert len(rows) == 3
    # Newest (highest id) stays on top.
    assert rows[0][1] == "item 4"
    assert rows[-1][1] == "item 2"


def test_search_filter(fresh_db, settings_cap):
    settings_cap()
    db.insert_record("apple banana")
    db.insert_record("cherry date")
    assert len(db.get_all_records("banana")) == 1
    assert len(db.get_all_records("nomatch")) == 0


def test_delete_record(fresh_db, settings_cap):
    settings_cap()
    rid, _ = db.insert_record("to delete")
    db.delete_record(rid)
    assert db.get_all_records() == []


def test_clear_all(fresh_db, settings_cap):
    settings_cap()
    db.insert_record("a")
    db.insert_record("b")
    db.clear_all_records()
    assert db.get_all_records() == []


def test_export_to_txt(fresh_db, settings_cap, tmp_path):
    settings_cap()
    db.insert_record("export me")
    out = tmp_path / "out.txt"
    db.export_to_txt(str(out))
    content = out.read_text(encoding="utf-8")
    assert "export me" in content
