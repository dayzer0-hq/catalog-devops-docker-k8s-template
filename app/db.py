"""The one place a database connection is opened.

Only the readiness check uses it today. If a ticket asks you to persist
something, this is the file the connection belongs in.
"""
from .config import Config


# ⚠️ WHEN YOU ADD A QUERY, PASS VALUES AS PARAMETERS — NEVER BUILD THE SQL.
#
#     conn.execute("select * from items where id = %s", (item_id,))   correct
#     conn.execute(f"select * from items where id = {item_id}")       injection
#
# The second line reads as the shorter one and is how SQL injection is
# written. This file is the first example of a query most people using this
# template will see, so it shows the safe form before anything else does.


def ping() -> tuple[bool, str]:
    """Return (ok, detail). Never raises — a readiness check must answer."""
    if not Config.DATABASE_URL:
        return False, "DATABASE_URL is not set"
    try:
        import psycopg
    except ImportError:
        return False, "psycopg is not installed"
    try:
        with psycopg.connect(
            Config.DATABASE_URL, connect_timeout=Config.DB_CONNECT_TIMEOUT
        ) as conn:
            conn.execute("select 1")
        return True, "ok"
    except Exception as exc:  # noqa: BLE001 - the detail is the payload
        return False, type(exc).__name__
