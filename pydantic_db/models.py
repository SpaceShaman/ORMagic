from typing import Self

from pydantic import BaseModel

from .sql_utils import execute_sql, get_sql_type


class NotExist(Exception):
    pass


class DBModel(BaseModel):
    id: int | None = None

    @classmethod
    def create_table(cls) -> None:
        sql = (
            f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} (id INTEGER PRIMARY KEY"
        )
        for field_name, field_info in cls.model_fields.items():
            if field_name == "id":
                continue
            field_type = get_sql_type(field_info.annotation)
            sql += f", {field_name} {field_type}"
            if field_info.is_required():
                sql += " NOT NULL"
        sql += ")"
        cursor = execute_sql(sql)
        cursor.connection.close()

    def save(self) -> None:
        fields = ", ".join(self.__annotations__.keys())
        values = ", ".join(
            f"'{getattr(self, field)}'" for field in self.__annotations__.keys()
        )
        sql = f"INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({values})"
        cursor = execute_sql(sql)
        cursor.connection.close()

    @classmethod
    def get(cls, **kwargs) -> Self:
        conditions = " AND ".join(
            f"{field}='{value}'" for field, value in kwargs.items()
        )
        sql = f"SELECT * FROM {cls.__name__.lower()} WHERE {conditions}"
        cursor = execute_sql(sql)
        data = cursor.fetchone()
        cursor.connection.close()
        if data:
            return cls(**dict(zip(cls.model_fields.keys(), data)))
        raise NotExist("Object does not exist")
