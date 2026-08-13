"""Compatibility helpers for the original database API."""

from db.database import clear_all_records, get_all_records, insert_record


def add_record(content_type, content=None, img_bytes=None, expire_days=30):
    if content_type != "text" or img_bytes is not None:
        raise ValueError("目前仅支持文本剪贴板记录")
    return insert_record(content or "")


def query_valid_records():
    return [(record_id, "text", content, None, created_at)
            for record_id, content, created_at in get_all_records()]


def clear_expire_data():
    return None


def delete_record(rid):
    raise NotImplementedError("当前界面暂未提供单条删除功能")


__all__ = ["add_record", "query_valid_records", "clear_all_records"]
