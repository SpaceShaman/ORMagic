import sqlite3
from sqlite3.dbapi2 import Cursor
from types import NoneType
from typing import Any, Literal, Union


def execute_sql(sql: str) -> Cursor:
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()
    cursor = cursor.execute(sql)
    connection.commit()
    return cursor


def convert_to_sql_type(annotation: Any) -> Literal["INTEGER", "TEXT"]:
    return "INTEGER" if annotation in [int, Union[int, NoneType]] else "TEXT"
