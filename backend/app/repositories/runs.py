import json
import sqlite3
from datetime import datetime, timezone


def insert(
    conn: sqlite3.Connection,
    kind: str,
    payload: dict,
    result: dict,
    account_id: int | None = None,
    pinned: bool = False,
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        """
        INSERT INTO calc_runs(kind, account_id, input_json, result_json, created_at, pinned, pinned_at)
        VALUES (?,?,?,?,?,?,?)
        """,
        (
            kind,
            account_id,
            json.dumps(payload, ensure_ascii=False),
            json.dumps(result, ensure_ascii=False),
            now,
            1 if pinned else 0,
            now if pinned else None,
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["pinned"] = bool(d.get("pinned"))
    return d


def list_recent(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    q = """
    SELECT id, kind, account_id, input_json, result_json, created_at,
           pinned, pinned_at, deleted_at
    FROM calc_runs
    WHERE deleted_at IS NULL
    ORDER BY pinned DESC, id DESC
    LIMIT ?
    """
    return [_row_to_dict(r) for r in conn.execute(q, (limit,)).fetchall()]


def list_page(
    conn: sqlite3.Connection,
    kind: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """分页列表；软删除记录默认不可见。钉选记录排在前面。"""
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    where = "WHERE deleted_at IS NULL"
    params: list = []
    if kind:
        where += " AND kind = ?"
        params.append(kind)
    total = conn.execute(f"SELECT COUNT(*) c FROM calc_runs {where}", params).fetchone()["c"]
    rows = conn.execute(
        f"""
        SELECT id, kind, account_id, input_json, result_json, created_at,
               pinned, pinned_at, deleted_at
        FROM calc_runs
        {where}
        ORDER BY pinned DESC, id DESC
        LIMIT ? OFFSET ?
        """,
        (*params, page_size, (page - 1) * page_size),
    ).fetchall()
    return {
        "items": [_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get(conn: sqlite3.Connection, run_id: int) -> dict | None:
    """按 id 查详情；软删除记录仍可读到完整快照。"""
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    return _row_to_dict(row) if row else None


def set_pinned(conn: sqlite3.Connection, run_id: int, pinned: bool) -> dict | None:
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    if not row:
        return None
    if pinned:
        conn.execute(
            "UPDATE calc_runs SET pinned=1, pinned_at=COALESCE(pinned_at, ?) WHERE id=?",
            (datetime.now(timezone.utc).isoformat(), run_id),
        )
    else:
        conn.execute("UPDATE calc_runs SET pinned=0, pinned_at=NULL WHERE id=?", (run_id,))
    conn.commit()
    return get(conn, run_id)


def soft_delete(conn: sqlite3.Connection, run_id: int) -> dict | None:
    row = conn.execute("SELECT id FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    if not row:
        return None
    conn.execute(
        "UPDATE calc_runs SET deleted_at=? WHERE id=? AND deleted_at IS NULL",
        (datetime.now(timezone.utc).isoformat(), run_id),
    )
    conn.commit()
    return get(conn, run_id)
