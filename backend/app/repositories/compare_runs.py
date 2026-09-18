import json
import sqlite3
from datetime import datetime, timezone

_LIST_COLS = (
    "id, kwh, plain_total, peak_total, delta, peak_factor, created_at, deleted_at"
)
_FULL_COLS = _LIST_COLS + ", segments_json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row: sqlite3.Row, *, with_segments: bool) -> dict:
    d = dict(row)
    if with_segments:
        raw = d.pop("segments_json", None)
        try:
            d["segments"] = json.loads(raw) if raw else {}
        except (ValueError, TypeError):
            d["segments"] = {}
    return d


def insert(conn: sqlite3.Connection, compare: dict) -> int:
    """钉选一次对比：peak_factor 与合计数字作为快照写入，后续不受 settings 改动影响。"""
    segments = {
        "plain_segments": compare.get("plain_segments", []),
        "peak_segments": compare.get("peak_segments", []),
    }
    cur = conn.execute(
        """
        INSERT INTO compare_runs(
            kwh, plain_total, peak_total, delta, peak_factor,
            segments_json, created_at, deleted_at
        ) VALUES (?,?,?,?,?,?,?,NULL)
        """,
        (
            compare["kwh"],
            compare["plain_total"],
            compare["peak_total"],
            compare["delta"],
            compare["peak_factor"],
            json.dumps(segments, ensure_ascii=False),
            _now(),
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def list_page(
    conn: sqlite3.Connection, limit: int = 20, offset: int = 0
) -> tuple[list[dict], int]:
    """分页列表：软删除的记录默认不可见。返回 (items, total)。"""
    total = conn.execute(
        "SELECT COUNT(*) c FROM compare_runs WHERE deleted_at IS NULL"
    ).fetchone()["c"]
    rows = conn.execute(
        f"SELECT {_LIST_COLS} FROM compare_runs WHERE deleted_at IS NULL "
        "ORDER BY id DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    return [_row_to_dict(r, with_segments=False) for r in rows], int(total)


def get(conn: sqlite3.Connection, run_id: int) -> dict | None:
    """按 id 查详情：含已软删除记录的完整快照。"""
    row = conn.execute(
        f"SELECT {_FULL_COLS} FROM compare_runs WHERE id=?", (run_id,)
    ).fetchone()
    return _row_to_dict(row, with_segments=True) if row else None


def soft_delete(conn: sqlite3.Connection, run_id: int) -> bool:
    cur = conn.execute(
        "UPDATE compare_runs SET deleted_at=? WHERE id=? AND deleted_at IS NULL",
        (_now(), run_id),
    )
    conn.commit()
    return cur.rowcount > 0
