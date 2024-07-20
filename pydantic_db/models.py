from pydantic import BaseModel

from .sql_utils import execute_sql, get_sql_type


class DBModel(BaseModel):
    @classmethod
    def create_table(cls) -> None:
        sql = (
            f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} (id INTEGER PRIMARY KEY"
        )
        for field_name, field_info in cls.model_fields.items():
            field_type = get_sql_type(field_info.annotation)
            sql += f", {field_name} {field_type}"
            if field_info.is_required():
                sql += " NOT NULL"
        sql += ")"
        execute_sql(sql)

    def save(self) -> None:
        fields = ", ".join(self.__annotations__.keys())
        values = ", ".join(
            f"'{getattr(self, field)}'" for field in self.__annotations__.keys()
        )
        sql = f"INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({values})"
        execute_sql(sql)
