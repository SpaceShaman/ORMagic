from sqlite3 import Connection, Cursor, connect

from ormagic.settings import Settings


def _create_connection() -> Connection:
    settings = Settings()
    connection = connect(settings.path, isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA journal_mode = {settings.journal_mode}")
    return connection


class SQLiteClient:
    def __init__(self) -> None:
        self.connection = _create_connection()
        self.cursor = self.connection.cursor()

    def execute(self, sql: str, parameters: list | None = None) -> Cursor:
        try:
            return (
                self.cursor.execute(sql, parameters)
                if parameters
                else self.cursor.execute(sql)
            )
        except Exception as e:
            self.connection.close()
            raise e

    def close(self) -> None:
        self.connection.close()

    def create_table(self, table_name: str, columns: list[str]) -> None:
        self.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")

    def is_table_exists(self, table_name: str) -> bool:
        cursor = self.execute(
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )
        return cursor.fetchone()[0] == 1

    def get_column_names(self, table_name: str) -> list[str]:
        cursor = self.execute(f"PRAGMA table_info({table_name})")
        return [column[1] for column in cursor.fetchall()]

    def drop_column(self, table_name: str, column_name: str) -> None:
        self.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")

    def rename_column(
        self, table_name: str, old_column_name: str, new_column_name: str
    ) -> None:
        self.execute(
            f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name}"
        )

    def add_column(self, table_name: str, column_name: str) -> None:
        self.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name}")

    def drop_table(self, table_name: str) -> None:
        self.execute(f"DROP TABLE {table_name}")
