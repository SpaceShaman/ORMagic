import sqlite3
from sqlite3.dbapi2 import Cursor
from types import NoneType
from typing import Any, Literal, Union, get_args


def execute_sql(sql: str) -> Cursor:
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()
    cursor = cursor.execute(sql)
    connection.commit()
    return cursor


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
