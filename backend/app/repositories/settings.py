import sqlite3

from app.config import DEFAULT_PEAK_FACTOR


def get_map(conn: sqlite3.Connection) -> dict[str, str]:
    return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}


def peak_factor(conn: sqlite3.Connection) -> float:
    row = conn.execute("SELECT value FROM settings WHERE key='peak_factor'").fetchone()
    if not row:
        return DEFAULT_PEAK_FACTOR
    return float(row["value"])


def set_peak_factor(conn: sqlite3.Connection, value: float) -> None:
    if value <= 0:
        raise ValueError("peak_factor must be positive")
    conn.execute(
        """
        INSERT INTO settings(key, value) VALUES ('peak_factor', ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """,
        (str(value),),
    )
    conn.commit()
