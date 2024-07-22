from typing import Self

from pydantic import BaseModel

from .sql_utils import execute_sql, get_sql_type


class ObjectNotFound(Exception):
    pass


class DBModel(BaseModel):
    id: int | None = None

    @classmethod
    def create_table(cls) -> None:
        columns = ["id INTEGER PRIMARY KEY"]
        for field_name, field_info in cls.model_fields.items():
            if field_name == "id":
                continue
            field_type = get_sql_type(field_info.annotation)
            column_def = f"{field_name} {field_type}"
            if field_info.is_required():
                column_def += " NOT NULL"
            columns.append(column_def)

        sql = (
            f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} ({', '.join(columns)})"
        )
        cursor = execute_sql(sql)
        cursor.connection.close()

    def save(self) -> Self:
        return self._update() if self.id else self._insert()

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
        raise ObjectNotFound

    def _insert(self) -> Self:
        model_dict = self.model_dump(exclude={"id"})
        fields = ", ".join(model_dict.keys())
        values = ", ".join(f"'{value}'" for value in model_dict.values())
        sql = f"INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({values})"
        cursor = execute_sql(sql)
        cursor.connection.close()
        self.id = cursor.lastrowid
        return self

    def _update(self) -> Self:
        model_dict = self.model_dump(exclude={"id"})
        fields = ", ".join(f"{field}='{value}'" for field, value in model_dict.items())
        sql = (
            f"UPDATE {self.__class__.__name__.lower()} SET {fields} WHERE id={self.id}"
        )
        cursor = execute_sql(sql)
        cursor.connection.close()
        if cursor.rowcount == 0:
            raise ObjectNotFound
        return self
