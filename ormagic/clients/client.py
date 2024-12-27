from typing import Protocol

from .sqlite import SQLiteClient


class Client(Protocol):
    def execute(self, sql: str, parameters: list | None = None) -> None: ...
    def create_table(self, table_name: str, columns: list[str]) -> None: ...
    def is_table_exists(self, table_name: str) -> bool: ...


def get_client() -> Client:
    return SQLiteClient()
