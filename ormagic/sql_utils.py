import sqlite3
from sqlite3 import Cursor


def get_cursor() -> Cursor:
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()
    cursor.executescript("PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;")
    return cursor


def execute_sql(sql: str, parms: list | None = None) -> Cursor:
    try:
        cursor = get_cursor()
        cursor = cursor.execute(sql) if parms is None else cursor.execute(sql, parms)
        cursor.connection.commit()
        return cursor
    except Exception as e:
        cursor.connection.close()
        raise e
