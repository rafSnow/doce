from contextlib import contextmanager
from app.db.connection import get_connection

@contextmanager
def transacao():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
