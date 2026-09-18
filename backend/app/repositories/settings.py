import sqlite3

from app.config import DEFAULT_PEAK_FACTOR


def get_map(conn: sqlite3.Connection) -> dict[str, str]:
    return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}


def peak_factor(conn: sqlite3.Connection) -> float:
    row = conn.execute("SELECT value FROM settings WHERE key='peak_factor'").fetchone()
    if not row:
        return DEFAULT_PEAK_FACTOR
    return float(row["value"])


def set_peak_factor(conn: sqlite3.Connection, factor: float) -> float:
    """更新全局尖峰系数；只影响之后的新对比，不改变已钉选快照。"""
    conn.execute(
        """
        INSERT INTO settings(key, value) VALUES ('peak_factor', ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """,
        (str(float(factor)),),
    )
    conn.commit()
    return float(factor)
