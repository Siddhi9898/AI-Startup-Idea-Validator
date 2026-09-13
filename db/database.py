"""
db/database.py
------------------
PostgreSQL persistence for every idea a user has validated (fixes:
"create a database that stores all the history of the users' ideas
using PostgreSQL"). This also replaces the old session-only History
tab: previously "history" was just a Python list in
st.session_state, so it vanished the moment the browser tab/session
was closed. It's now a real table, so history survives restarts and
can be queried across sessions.

Design notes:
- Kept deliberately simple (raw psycopg2 + one table), consistent
  with the rest of this codebase's "deterministic, no hidden magic"
  style - no ORM layer needed for one table.
- The full pipeline result (every agent's output) is stored as JSONB
  in `full_result`, plus a handful of plain columns that are
  genuinely useful to filter/sort/list on without unpacking JSON
  every time (idea_name, viability_score, submitted_at, ...).
- Every public function fails SOFT: if Postgres isn't configured or
  isn't reachable, these functions log a warning and return an
  empty/None result rather than crashing the validation pipeline.
  Persistence is a nice-to-have on top of a working validator, not a
  hard dependency of it.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from app.config import DATABASE_URL, PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD

logger = logging.getLogger("db.database")

try:
    import psycopg2
    import psycopg2.extras
    _PSYCOPG2_AVAILABLE = True
except ImportError:  # pragma: no cover - only hit if the dependency isn't installed
    _PSYCOPG2_AVAILABLE = False


_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS validated_ideas (
    id SERIAL PRIMARY KEY,
    idea_name TEXT NOT NULL DEFAULT 'Untitled Idea',
    idea_text TEXT NOT NULL,
    industry TEXT,
    target_market TEXT,
    budget TEXT,
    timeline TEXT,
    viability_score NUMERIC,
    verdict TEXT,
    quick_summary TEXT,
    report_markdown TEXT,
    full_result JSONB NOT NULL,
    submitted_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_validated_ideas_submitted_at ON validated_ideas (submitted_at DESC);

-- Chat summary: a running, compressed digest of the advisor
-- conversation for this idea (see advisor_messages below for why
-- this exists) - kept on the parent row since there's only ever one
-- summary per idea.
ALTER TABLE validated_ideas ADD COLUMN IF NOT EXISTS chat_summary TEXT;

-- Advisor Q&A history (fixes: "save the chats asked by the user and
-- answered by the advisor, but only wanted/related questions -
-- summarize so the chat history doesn't grow unbounded").
-- Only RELEVANT question/answer pairs are ever inserted here - see
-- agents/conversational_advisor.py's relevance check. Off-topic
-- questions are still answered live in the session, they're just
-- never written here. Once a conversation grows past a threshold,
-- the oldest rows get folded into validated_ideas.chat_summary and
-- deleted, keeping this table small per-idea (see
-- db/database.py:compress_advisor_messages()).
CREATE TABLE IF NOT EXISTS advisor_messages (
    id SERIAL PRIMARY KEY,
    validation_id INTEGER NOT NULL REFERENCES validated_ideas(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_advisor_messages_validation_id ON advisor_messages (validation_id, created_at);
"""


def _get_connection():
    if not _PSYCOPG2_AVAILABLE:
        raise RuntimeError(
            "psycopg2 is not installed. Run: pip install psycopg2-binary"
        )
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASSWORD,
    )


def init_db() -> bool:
    """Creates the validated_ideas table if it doesn't already exist.
    Safe to call on every app startup. Returns True on success, False
    if the database isn't reachable/configured (never raises)."""
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(_CREATE_TABLE_SQL)
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Postgres init_db skipped - database not reachable: %s", e)
        return False


def save_validation(result: dict, meta: Optional[dict] = None) -> Optional[int]:
    """
    Persists one completed pipeline run. `result` is the full
    SharedState.to_dict() output; `meta` is the optional
    {"budget": ..., "timeline": ...} the UI collects alongside the
    idea. Returns the new row's id, or None if it couldn't be saved
    (database unreachable) - callers should treat that as
    non-fatal, since the in-memory result is still usable either way.
    """
    meta = meta or {}
    extracted = result.get("extracted", {})
    viability = result.get("viability_score", {})

    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO validated_ideas
                        (idea_name, idea_text, industry, target_market, budget, timeline,
                         viability_score, verdict, quick_summary, report_markdown, full_result, submitted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        extracted.get("idea_name") or "Untitled Idea",
                        result.get("idea_text", ""),
                        extracted.get("industry", ""),
                        extracted.get("location", ""),
                        meta.get("budget", ""),
                        meta.get("timeline", ""),
                        viability.get("overall_score"),
                        viability.get("verdict", ""),
                        result.get("quick_summary", ""),
                        result.get("report", ""),
                        json.dumps(result),
                        meta.get("submitted_at") or datetime.now(),
                    ),
                )
                new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Could not save validation to Postgres: %s", e)
        return None


def list_validations(limit: int = 50) -> list:
    """Returns lightweight summaries (newest first) for the History
    tab - NOT the full JSON blob, so listing stays fast even with a
    large history. Returns [] if the database isn't reachable."""
    try:
        conn = _get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, idea_name, industry, target_market, budget, timeline,
                           viability_score, verdict, quick_summary, submitted_at
                    FROM validated_ideas
                    ORDER BY submitted_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Could not list validations from Postgres: %s", e)
        return []


def get_validation(validation_id: int) -> Optional[dict]:
    """Returns the full stored pipeline result dict for one past
    validation (used to re-render tabs / regenerate a PDF), or None
    if not found / database unreachable."""
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT full_result FROM validated_ideas WHERE id = %s",
                    (validation_id,),
                )
                row = cur.fetchone()
                return row[0] if row else None
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Could not fetch validation %s from Postgres: %s", validation_id, e)
        return None


def delete_validation(validation_id: int) -> bool:
    """Deletes one past validation by id. Returns True on success."""
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM validated_ideas WHERE id = %s", (validation_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Could not delete validation %s from Postgres: %s", validation_id, e)
        return False


# --- Advisor chat history -------------------------------------------------
# Only relevant Q&A pairs get here (see agents/conversational_advisor.py's
# relevance check) - off-topic questions are answered live but never saved.

def save_advisor_message(validation_id: int, role: str, content: str) -> Optional[int]:
    """Persists ONE chat turn (role is 'user' or 'assistant') tied to a
    validation. Returns the new row id, or None if unreachable/no
    validation_id (e.g. this session's validation wasn't saved to the
    DB in the first place) - never raises."""
    if not validation_id:
        return None
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO advisor_messages (validation_id, role, content)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (validation_id, role, content),
                )
                new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Could not save advisor message to Postgres: %s", e)
        return None


def get_advisor_messages(validation_id: int) -> list:
    """Returns raw (uncompressed) chat turns for a validation, oldest
    first. Returns [] if none exist or the database is unreachable."""
    if not validation_id:
        return []
    try:
        conn = _get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, role, content, created_at
                    FROM advisor_messages
                    WHERE validation_id = %s
                    ORDER BY created_at ASC
                    """,
                    (validation_id,),
                )
                return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Could not fetch advisor messages for %s: %s", validation_id, e)
        return []


def get_chat_summary(validation_id: int) -> Optional[str]:
    """Returns the running compressed chat summary for a validation
    (or None if there isn't one yet / DB unreachable)."""
    if not validation_id:
        return None
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT chat_summary FROM validated_ideas WHERE id = %s",
                    (validation_id,),
                )
                row = cur.fetchone()
                return row[0] if row else None
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Could not fetch chat summary for %s: %s", validation_id, e)
        return None


def compress_advisor_messages(validation_id: int, new_summary: str, keep_message_ids: list) -> bool:
    """
    Replaces the running chat_summary with `new_summary` (already
    computed by the caller - this function does no summarizing
    itself, it's pure persistence) and deletes every advisor_messages
    row for this validation EXCEPT the ids in `keep_message_ids`
    (the most recent few turns, kept raw for immediate context).
    This is what keeps the chat table from growing unbounded per
    idea while still preserving the gist of older turns. Returns
    True on success.
    """
    if not validation_id:
        return False
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE validated_ideas SET chat_summary = %s WHERE id = %s",
                    (new_summary, validation_id),
                )
                if keep_message_ids:
                    cur.execute(
                        """
                        DELETE FROM advisor_messages
                        WHERE validation_id = %s AND id NOT IN %s
                        """,
                        (validation_id, tuple(keep_message_ids)),
                    )
                else:
                    cur.execute(
                        "DELETE FROM advisor_messages WHERE validation_id = %s",
                        (validation_id,),
                    )
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Could not compress advisor messages for %s: %s", validation_id, e)
        return False
