import os
from typing import Protocol

from pydantic import BaseModel


class Column(BaseModel):
    name: str
    type: str
    nullable: bool = False
    default: str | None = None
    is_primary_key: bool = False


class ForeignKey(BaseModel):
    column_name: str
    foreign_table_name: str
    column_name_in_foreign_table: str
    on_delete: str = "CASCADE"
    on_update: str = "CASCADE"


class Assertor(Protocol):
    def assert_table_schema(self, table_name: str, expected_columns: list[Column]): ...

    def assert_foreign_keys(
        self, table_name: str, expected_foreign_keys: list[ForeignKey]
    ): ...


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

    def assert_foreign_keys(
        self, table_name: str, expected_foreign_keys: list[ForeignKey]
    ):
        foreign_keys = self._get_foreign_keys(table_name)
        assert len(foreign_keys) == len(expected_foreign_keys)
        for i, foreign_key in enumerate(foreign_keys):
            assert foreign_key[2] == expected_foreign_keys[i].foreign_table_name
            assert foreign_key[3] == expected_foreign_keys[i].column_name
            assert (
                foreign_key[4] == expected_foreign_keys[i].column_name_in_foreign_table
            )
            assert foreign_key[5] == expected_foreign_keys[i].on_delete
            assert foreign_key[6] == expected_foreign_keys[i].on_update

    def _get_foreign_keys(self, table_name):
        return self.cursor.execute(f"PRAGMA foreign_key_list({table_name});").fetchall()

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
            assert column[3] == (
                f"{expected_column.default}::{expected_column.type.lower()}"
                if expected_column.default
                else None
            )
            assert column[4] == expected_column.is_primary_key

    def assert_foreign_keys(
        self, table_name: str, expected_foreign_keys: list[ForeignKey]
    ):
        foreign_keys = self._get_foreign_keys(table_name)
        assert len(foreign_keys) == len(expected_foreign_keys)
        for foreign_key in foreign_keys:
            expected_foreign_key = next(
                filter(
                    lambda fk: fk.column_name == foreign_key[0], expected_foreign_keys
                )
            )
            assert foreign_key[0] == expected_foreign_key.column_name
            assert foreign_key[1] == expected_foreign_key.foreign_table_name
            assert foreign_key[2] == expected_foreign_key.column_name_in_foreign_table
            assert foreign_key[3] == expected_foreign_key.on_delete
            assert foreign_key[4] == expected_foreign_key.on_update

    def _get_foreign_keys(self, table_name):
        self.cursor.execute(
            """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS column_name_in_foreign_table,
                rc.delete_rule AS on_delete,
                rc.update_rule AS on_update
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            JOIN information_schema.referential_constraints AS rc
            ON rc.constraint_name = tc.constraint_name
            WHERE tc.table_name = %s
            """,
            (table_name,),
        )
        return self.cursor.fetchall()

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


def assert_table_schema(cursor, table_name: str, expected_columns: list[Column]):
    assertor = _get_assertor(cursor)
    assertor.assert_table_schema(table_name, expected_columns)


def assert_foreign_keys(
    cursor, table_name: str, expected_foreign_keys: list[ForeignKey]
):
    assertor = _get_assertor(cursor)
    assertor.assert_foreign_keys(table_name, expected_foreign_keys)
