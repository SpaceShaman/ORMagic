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


def get_assertor(cursor) -> Assertor:
    if _is_sqlite():
        from .sqlite import SQLiteAssertor

        return SQLiteAssertor(cursor)
    if _is_postgres():
        from .postgres import PostgresAssertor

        return PostgresAssertor(cursor)
    raise ValueError("Unsupported database")


def _is_sqlite() -> bool:
    return os.getenv("ORMAGIC_DATABASE_URL", "").startswith("sqlite")


def _is_postgres() -> bool:
    return os.getenv("ORMAGIC_DATABASE_URL", "").startswith("postgresql")
