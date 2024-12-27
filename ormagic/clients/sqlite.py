from contextlib import contextmanager
from sqlite3 import Connection, Cursor, connect
from typing import Generator

from ormagic.settings import Settings


def _create_connection() -> Connection:
    settings = Settings()
    connection = connect(settings.path, isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA journal_mode = {settings.journal_mode}")
    return connection


@contextmanager
def _get_cursor() -> Generator[Cursor, None, None]:
    connection = _create_connection()
    try:
        yield connection.cursor()
    finally:
        connection.close()


class SQLiteClient:
    def execute(self, sql: str, parameters: list | None = None) -> None:
        with _get_cursor() as cursor:
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)

    def create_table(self, table_name: str, columns: list[str]) -> None:
        self.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")

    def is_table_exists(self, table_name: str) -> bool:
        with _get_cursor() as cursor:
            cursor.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            )
            return cursor.fetchone()[0] == 1
