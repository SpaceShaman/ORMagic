import os
from abc import ABC, abstractmethod
from sqlite3 import connect
from typing import Protocol


class Cursor(Protocol):
    def execute(self, sql: str, parameters: list = ..., /) -> "Cursor": ...
    def fetchone(self) -> tuple: ...
    def fetchall(self) -> list[tuple]: ...
    @property
    def lastrowid(self) -> int | None: ...
    @property
    def rowcount(self) -> int: ...


class Connection(Protocol):
    def cursor(self) -> Cursor: ...
    def execute(self, sql: str, parameters: list = ..., /) -> Cursor: ...
    def close(self) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


class ConnectionCreator(ABC):
    @abstractmethod
    def create_connection(self) -> Connection: ...


class SQLiteConnectionCreator(ConnectionCreator):
    def create_connection(self) -> Connection:
        database = os.environ.get("ORMAGIC_DATABASE", "sqlite://db.sqlite3").replace(
            "sqlite://", ""
        )
        connection = connect(database, isolation_level=None)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection


class DatabaseNotSupported(Exception):
    pass


def create_connection() -> Connection:
    database = os.environ.get("ORMAGIC_DATABASE", "sqlite://db.sqlite3")
    if database.startswith("sqlite://"):
        return SQLiteConnectionCreator().create_connection()
    else:
        raise DatabaseNotSupported(f"Database {database} is not supported")
