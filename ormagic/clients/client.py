from contextlib import contextmanager
from typing import Any, Generator, Protocol

from ormagic.settings import Settings


class DatabaseNotSupported(Exception):
    pass


class Client(Protocol):
    def create_connection(self) -> Any: ...
    def execute(self, sql: str, parameters: list | None = None) -> Any: ...
    def close(self) -> None: ...
    def rollback(self) -> None: ...
    def commit(self) -> None: ...
    def create_table(self, table_name: str, columns: list[str]) -> None: ...
    def is_table_exists(self, table_name: str) -> bool: ...
    def get_column_names(self, table_name: str) -> list[str]: ...
    def drop_column(self, table_name: str, column_name: str) -> None: ...

    def rename_column(
        self, table_name: str, old_column_name: str, new_column_name: str
    ) -> None: ...
    def add_column(self, table_name: str, column_name: str) -> None: ...
    def drop_table(self, table_name: str) -> None: ...

    def update_rows(
        self, table_name: str, fields: dict[str, str], where: str
    ) -> None: ...
    def delete_rows(self, table_name: str, where: str) -> None: ...

    def insert_row(
        self, table_name: str, columns: list[str], values: list[str]
    ) -> None: ...

    def insert_row_and_get_id(
        self, table_name: str, columns: list[str], values: list[str], id_column: str
    ) -> int: ...

    def is_row_exists(self, table_name: str, where: str) -> bool: ...
    def fetchone(self, sql: str, parameters: list[Any] | None = None) -> Any: ...
    def fetchall(self, sql: str, parameters: list[Any] | None = None) -> list[Any]: ...


def get_client() -> Client:
    settings = Settings()
    if settings.db_type == "sqlite":
        from .sqlite import SQLiteClient

        return SQLiteClient()
    elif settings.db_type == "postgresql":
        from .postgres import PostgresClient

        return PostgresClient()
    raise DatabaseNotSupported(f"{settings.db_type} is not supported")


@contextmanager
def client_context() -> Generator[Client, None, None]:
    from ormagic.transactions import transaction

    if transaction._is_transaction:
        yield transaction._client
    else:
        client = get_client()
        client.create_connection()
        try:
            yield client
        finally:
            client.close()
