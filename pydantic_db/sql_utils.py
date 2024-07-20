import sqlite3
from types import NoneType
from typing import Any, Literal, Union


def execute_sql(sql: str) -> None:
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    con.close()


def get_sql_type(annotation: Any) -> Literal["INTEGER", "TEXT"]:
    return "INTEGER" if annotation in [int, Union[int, NoneType]] else "TEXT"
