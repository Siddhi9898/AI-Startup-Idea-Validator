"""
tools/offline_cache.py
--------------------------
Fixes: "if the user is offline, the history should be available to
see anytime" - not just within the current browser session.

Previously, history had an in-memory (st.session_state) fallback: if
a later Postgres fetch failed, the LAST-successfully-loaded copy from
earlier in that same session was shown instead of an empty list. That
only helps if the browser tab has stayed open since the last
successful fetch - closing the tab, restarting the app, or a DB
outage before the founder even loads a page today would still show
nothing.

This adds a small disk-backed cache (one JSON file per user, under
.cache/history/) that's updated every time a real fetch succeeds, and
read back whenever a fetch fails - so "yesterday's history" is still
visible today even if Postgres is completely unreachable right now
and the browser session is brand new. This is the practical ceiling
for "offline" in a server-rendered Streamlit app - true offline (no
network to the Streamlit server itself) isn't achievable without
turning this into a different kind of app (a PWA with a service
worker); see the note in ui/streamlit_app.py for that caveat.
"""

import os
import json
import logging
from datetime import datetime, date
from decimal import Decimal

logger = logging.getLogger("tools.offline_cache")

_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache", "history")


def _cache_path(user_id: int) -> str:
    return os.path.join(_CACHE_DIR, f"user_{user_id}.json")


def _json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


def save_history_cache(user_id: int, rows: list) -> bool:
    """Writes this user's most recently fetched history list to disk.
    Called every time a live Postgres fetch succeeds. Never raises -
    a caching failure should never break the app."""
    if not user_id or rows is None:
        return False
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        with open(_cache_path(user_id), "w", encoding="utf-8") as f:
            json.dump(rows, f, default=_json_default)
        return True
    except Exception as e:
        logger.warning("Could not save offline history cache for user %s: %s", user_id, e)
        return False


def load_history_cache(user_id: int) -> list:
    """Reads back this user's last-cached history list, or [] if none
    exists yet / it can't be read. Datetime fields come back as plain
    ISO strings (not datetime objects) - callers already handle that
    (see ui/streamlit_app.py's submitted_at display logic)."""
    if not user_id:
        return []
    try:
        path = _cache_path(user_id)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Could not load offline history cache for user %s: %s", user_id, e)
        return []
