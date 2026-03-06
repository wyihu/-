import sqlite3
from typing import Any

from backend.core.config import DB_PATH
from backend.db.schema import SCHEMA_SQL


PROVIDER_JOBS_REQUIRED_COLUMNS = {
    "provider_job_id": "TEXT",
    "outputs_json": "TEXT DEFAULT '[]'",
    "error_message": "TEXT DEFAULT ''",
    "updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
    "retry_count": "INTEGER DEFAULT 0",
    "max_retries": "INTEGER DEFAULT 0",
    "fallback_provider": "TEXT DEFAULT ''",
    "fallback_model_key": "TEXT DEFAULT ''",
    "active_provider": "TEXT DEFAULT ''",
    "active_model_key": "TEXT DEFAULT ''",
    "status_history_json": "TEXT DEFAULT '[]'",
}



def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _migrate_provider_jobs_columns(conn: sqlite3.Connection) -> None:
    rows = conn.execute("PRAGMA table_info(provider_jobs)").fetchall()
    existing = {row[1] for row in rows}
    for column_name, ddl in PROVIDER_JOBS_REQUIRED_COLUMNS.items():
        if column_name not in existing:
            conn.execute(f"ALTER TABLE provider_jobs ADD COLUMN {column_name} {ddl}")


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)
        _migrate_provider_jobs_columns(conn)
        conn.commit()


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def execute(query: str, params: tuple[Any, ...] = ()) -> int:
    with get_connection() as conn:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.lastrowid
