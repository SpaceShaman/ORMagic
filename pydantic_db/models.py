import sqlite3
from types import NoneType
from typing import Union

from pydantic import BaseModel


class DBModel(BaseModel):
    @classmethod
    def create_table(cls):
        sql = (
            f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} (id INTEGER PRIMARY KEY"
        )
        for name, field_info in cls.model_fields.items():
            sql += f", {name} {cls._get_sql_type(field_info.annotation)}"
            if field_info.is_required():
                sql += " NOT NULL"
        sql += ")"
        cls._execute_sql(sql)

    def save(self):
        fields = ", ".join(self.__annotations__.keys())
        values = ", ".join(
            f"'{getattr(self, field)}'" for field in self.__annotations__.keys()
        )
        sql = f"INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({values})"
        self._execute_sql(sql)

    @classmethod
    def _execute_sql(cls, sql: str):
        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        con.close()

    @classmethod
    def _get_sql_type(cls, annotation):
        return "INTEGER" if annotation in [int, Union[int, NoneType]] else "TEXT"
