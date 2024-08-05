import sqlite3
from sqlite3 import Cursor
from types import NoneType
from typing import Any, Literal, Union, get_args


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


def convert_to_sql_type(annotation: Any) -> Literal["INTEGER", "TEXT"]:
    from .models import DBModel

    if annotation in [int, Union[int, NoneType]]:
        return "INTEGER"
    types_tuple = get_args(annotation)
    if not types_tuple and issubclass(annotation, DBModel):
        return "INTEGER"
    if types_tuple and issubclass(types_tuple[0], DBModel):
        return "INTEGER"
    return "TEXT"
