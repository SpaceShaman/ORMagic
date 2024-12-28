import os
from typing import Protocol

from pydantic import BaseModel


class Column(BaseModel):
    name: str
    type: str
    nullable: bool = False
    default: str | None = None
    is_primary_key: bool = False


class Assertor(Protocol):
    def assert_table_schema(self, table_name: str, expected_columns: list[Column]): ...


class SQLiteAssertor:
    def __init__(self, cursor):
        self.cursor = cursor

    def assert_table_schema(self, table_name: str, expected_columns: list[Column]):
        columns = self._get_table_columns(table_name)
        assert len(columns) == len(expected_columns)
        for i, column in enumerate(columns):
            assert column[1] == expected_columns[i].name
            assert column[2] == expected_columns[i].type
            assert column[3] == 0 if expected_columns[i].nullable else 1
            assert column[4] == expected_columns[i].default
            assert column[5] == expected_columns[i].is_primary_key

    def _get_table_columns(self, table_name):
        return self.cursor.execute(f"PRAGMA table_info({table_name});").fetchall()


class PostgresAssertor:
    def __init__(self, cursor):
        self.cursor = cursor

    def assert_table_schema(self, table_name: str, expected_columns: list[Column]):
        columns = self._get_table_columns(table_name)
        assert len(columns) == len(expected_columns)
        for column in columns:
            expected_column = next(
                filter(lambda c: c.name == column[0], expected_columns)
            )
            assert column[0] == expected_column.name
            assert column[1] == expected_column.type.lower()
            assert column[2] == "YES" if expected_column.nullable else "NO"
            assert column[3] == expected_column.default
            assert column[4] == expected_column.is_primary_key

    def _get_table_columns(self, table_name):
        self.cursor.execute(
            """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                (SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_name = kcu.table_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND kcu.column_name = c.column_name
                    AND kcu.table_name = %s
                )) AS is_primary_key
            FROM information_schema.columns c
            WHERE table_name = %s;
            """,
            (table_name, table_name),
        )
        return self.cursor.fetchall()


def assert_table_schema(cursor, table_name: str, expected_columns: list[Column]):
    assertor = _get_assertor(cursor)
    assertor.assert_table_schema(table_name, expected_columns)


def _get_assertor(cursor) -> Assertor:
    if _is_sqlite():
        return SQLiteAssertor(cursor)
    if _is_postgres():
        return PostgresAssertor(cursor)
    raise ValueError("Unsupported database")


def _is_sqlite() -> bool:
    return os.getenv("ORMAGIC_DATABASE_URL", "").startswith("sqlite")


def _is_postgres() -> bool:
    return os.getenv("ORMAGIC_DATABASE_URL", "").startswith("postgresql")
