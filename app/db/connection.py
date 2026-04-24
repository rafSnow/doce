import sqlite3
import os
import sys

_conn: sqlite3.Connection | None = None


def get_db_path() -> str:
    if getattr(sys, 'frozen', False):
        # No modo executável pelo PyInstaller, salva na mesma pasta de onde o .exe está sendo executado
        base_dir = os.path.dirname(sys.executable)
    else:
        # Em modo de desenvolvimento, salva na raiz do projeto
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

    return os.path.join(base_dir, "confeitaria.db")

def reset_connection() -> None:
    global _conn
    if _conn is not None:
        try:
            _conn.close()
        except:
            pass
        _conn = None

def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        db_path = get_db_path()
        _conn = sqlite3.connect(db_path, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys = ON")
    return _conn
