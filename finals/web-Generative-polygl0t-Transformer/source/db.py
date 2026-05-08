from __future__ import annotations

import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path


SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        if table_exists(conn, "player_sessions"):
            ensure_column(conn, "player_sessions", "user_id", "TEXT")
        conn.executescript(SCHEMA_PATH.read_text())
        ensure_column(conn, "player_sessions", "user_id", "TEXT")
        conn.commit()


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table_name,),
    ).fetchone()
    return row is not None


def ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, column_sql: str) -> None:
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    if any(column["name"] == column_name for column in columns):
        return
    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}")


@contextmanager
def transaction(db_path: str):
    conn = connect(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query_one(db_path: str, sql: str, params: tuple = ()):
    with connect(db_path) as conn:
        return conn.execute(sql, params).fetchone()


def query_all(db_path: str, sql: str, params: tuple = ()):
    with connect(db_path) as conn:
        return conn.execute(sql, params).fetchall()


def execute(db_path: str, sql: str, params: tuple = ()) -> int:
    with connect(db_path) as conn:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.rowcount


def finalize_expired_claims(
    db_path: str,
    now: int,
    fallback_source: str,
    fallback_html: str,
    fallback_author: str,
) -> int:
    with transaction(db_path) as conn:
        expired = conn.execute(
            """
            SELECT q.chat_id,
                   COALESCE(d.content_source, '') AS draft_source,
                   COALESCE(d.content_html, '') AS draft_html
            FROM queue_items q
            LEFT JOIN drafts d ON d.chat_id = q.chat_id
            WHERE q.status = 'claimed'
              AND q.claim_until IS NOT NULL
              AND q.claim_until < ?
            """,
            (now,),
        ).fetchall()

        for row in expired:
            answer_source = row["draft_source"] or fallback_source
            answer_html = row["draft_html"] or fallback_html
            conn.execute(
                """
                UPDATE chats
                SET status = 'answered',
                    answer_source = ?,
                    answer_html = ?,
                    answer_author = ?,
                    updated_at = ?,
                    answered_at = ?
                WHERE id = ?
                """,
                (answer_source, answer_html, fallback_author, now, now, row["chat_id"]),
            )
            conn.execute(
                """
                UPDATE queue_items
                SET status = 'answered',
                    updated_at = ?
                WHERE chat_id = ?
                """,
                (now, row["chat_id"]),
            )

        return len(expired)


def claim_next_human_chat(db_path: str, claimed_by: str, lease_seconds: int, now: int):
    with transaction(db_path) as conn:
        row = conn.execute(
            """
            SELECT c.id,
                   c.locale,
                   c.prompt_html,
                   c.prompt_source,
                   c.full_url,
                   q.created_at
            FROM queue_items q
            JOIN chats c ON c.id = q.chat_id
            WHERE q.status = 'queued'
            ORDER BY q.created_at ASC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None

        claim_token = uuid.uuid4().hex
        claim_until = now + lease_seconds
        result = conn.execute(
            """
            UPDATE queue_items
            SET status = 'claimed',
                claimed_by = ?,
                claim_token = ?,
                claim_until = ?,
                updated_at = ?
            WHERE chat_id = ?
              AND status = 'queued'
            """,
            (claimed_by, claim_token, claim_until, now, row["id"]),
        )
        if result.rowcount != 1:
            return None

        conn.execute(
            """
            UPDATE chats
            SET status = 'claimed',
                updated_at = ?
            WHERE id = ?
            """,
            (now, row["id"]),
        )
        conn.execute(
            """
            INSERT INTO drafts (chat_id, content_source, content_html, updated_at)
            VALUES (?, '', '', ?)
            ON CONFLICT(chat_id) DO NOTHING
            """,
            (row["id"], now),
        )

        payload = dict(row)
        payload["claim_token"] = claim_token
        payload["claim_until"] = claim_until
        return payload


def extend_claim(
    db_path: str,
    chat_id: str,
    claim_token: str,
    lease_seconds: int,
    now: int,
    draft_source: str,
    draft_html: str,
):
    with transaction(db_path) as conn:
        row = conn.execute(
            """
            SELECT chat_id
            FROM queue_items
            WHERE chat_id = ?
              AND status = 'claimed'
              AND claim_token = ?
            """,
            (chat_id, claim_token),
        ).fetchone()
        if row is None:
            return None

        claim_until = now + lease_seconds

        conn.execute(
            """
            UPDATE queue_items
            SET claim_until = ?,
                updated_at = ?
            WHERE chat_id = ?
            """,
            (claim_until, now, chat_id),
        )
        conn.execute(
            """
            INSERT INTO drafts (chat_id, content_source, content_html, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                content_source = excluded.content_source,
                content_html = excluded.content_html,
                updated_at = excluded.updated_at
            """,
            (chat_id, draft_source, draft_html, now),
        )
        return claim_until


def finalize_claim(
    db_path: str,
    chat_id: str,
    claim_token: str,
    answer_source: str,
    answer_html: str,
    answer_author: str,
    now: int,
) -> bool:
    with transaction(db_path) as conn:
        row = conn.execute(
            """
            SELECT chat_id
            FROM queue_items
            WHERE chat_id = ?
              AND status = 'claimed'
              AND claim_token = ?
            """,
            (chat_id, claim_token),
        ).fetchone()
        if row is None:
            return False

        conn.execute(
            """
            UPDATE chats
            SET status = 'answered',
                answer_source = ?,
                answer_html = ?,
                answer_author = ?,
                updated_at = ?,
                answered_at = ?
            WHERE id = ?
            """,
            (answer_source, answer_html, answer_author, now, now, chat_id),
        )
        conn.execute(
            """
            UPDATE queue_items
            SET status = 'answered',
                updated_at = ?
            WHERE chat_id = ?
            """,
            (now, chat_id),
        )
        conn.execute("DELETE FROM drafts WHERE chat_id = ?", (chat_id,))
        return True


def release_claim(
    db_path: str,
    chat_id: str,
    claim_token: str,
    now: int,
) -> bool:
    with transaction(db_path) as conn:
        row = conn.execute(
            """
            SELECT chat_id
            FROM queue_items
            WHERE chat_id = ?
              AND status = 'claimed'
              AND claim_token = ?
            """,
            (chat_id, claim_token),
        ).fetchone()
        if row is None:
            return False

        conn.execute(
            """
            UPDATE queue_items
            SET status = 'queued',
                claimed_by = NULL,
                claim_token = NULL,
                claim_until = NULL,
                updated_at = ?
            WHERE chat_id = ?
            """,
            (now, chat_id),
        )
        conn.execute("DELETE FROM drafts WHERE chat_id = ?", (chat_id,))
        return True


def claim_next_bot_job(db_path: str, now: int):
    with transaction(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, full_url
            FROM chats
            WHERE target = 'bot'
              AND status = 'bot_pending'
            ORDER BY dispatched_at ASC, created_at ASC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None

        result = conn.execute(
            """
            UPDATE chats
            SET status = 'bot_processing',
                updated_at = ?
            WHERE id = ?
              AND status = 'bot_pending'
            """,
            (now, row["id"]),
        )
        if result.rowcount != 1:
            return None

        return dict(row)


def complete_bot_job(
    db_path: str,
    chat_id: str,
    answer_source: str,
    answer_html: str,
    answer_author: str,
    now: int,
) -> bool:
    with transaction(db_path) as conn:
        result = conn.execute(
            """
            UPDATE chats
            SET status = 'answered',
                answer_source = ?,
                answer_html = ?,
                answer_author = ?,
                updated_at = ?,
                answered_at = ?
            WHERE id = ?
              AND status IN ('bot_processing', 'bot_pending')
            """,
            (answer_source, answer_html, answer_author, now, now, chat_id),
        )
        return result.rowcount == 1


def fail_bot_job(db_path: str, chat_id: str, now: int) -> bool:
    with transaction(db_path) as conn:
        result = conn.execute(
            """
            UPDATE chats
            SET status = 'bot_failed',
                updated_at = ?
            WHERE id = ?
              AND status IN ('bot_processing', 'bot_pending')
            """,
            (now, chat_id),
        )
        return result.rowcount == 1


def seconds_now() -> int:
    return int(time.time())
