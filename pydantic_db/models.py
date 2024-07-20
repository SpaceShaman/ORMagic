import sqlite3

from pydantic import BaseModel


class DBModel(BaseModel):
    @classmethod
    def create_table(cls):
        sql = (
            f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} (id INTEGER PRIMARY KEY"
        )
        for name, value in cls.__annotations__.items():
            if value.__name__ == "str":
                sql += f", {name} TEXT NOT NULL"
            elif value.__name__ == "int":
                sql += f", {name} INTEGER NOT NULL"
            else:
                raise ValueError(f"Unsupported type {value.__name__}")
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
