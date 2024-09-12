import sqlite3
from contextlib import contextmanager
from sqlite3 import Cursor
from typing import Any, Generator


@contextmanager
def get_cursor() -> Generator[Cursor, Any, None]:
    connection = sqlite3.connect("db.sqlite3", isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    try:
        yield connection.cursor()
    finally:
        connection.close()
