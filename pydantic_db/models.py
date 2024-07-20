import sqlite3
from types import NoneType
from typing import Any, Literal, Union

from pydantic import BaseModel


class DBModel(BaseModel):
    @classmethod
    def create_table(cls) -> None:
        sql = (
            f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} (id INTEGER PRIMARY KEY"
        )
        for field_name, field_info in cls.model_fields.items():
            field_type = cls._get_sql_type(field_info.annotation)
            sql += f", {field_name} {field_type}"
            if field_info.is_required():
                sql += " NOT NULL"
        sql += ")"
        cls._execute_sql(sql)

    def save(self) -> None:
        fields = ", ".join(self.__annotations__.keys())
        values = ", ".join(
            f"'{getattr(self, field)}'" for field in self.__annotations__.keys()
        )
        sql = f"INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({values})"
        self._execute_sql(sql)

    @classmethod
    def _execute_sql(cls, sql: str) -> None:
        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        con.close()

    @classmethod
    def _get_sql_type(cls, annotation: Any) -> Literal["INTEGER", "TEXT"]:
        return "INTEGER" if annotation in [int, Union[int, NoneType]] else "TEXT"
