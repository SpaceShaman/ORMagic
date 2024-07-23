from typing import Self, get_args

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from .sql_utils import convert_to_sql_type, execute_sql


class ObjectNotFound(Exception):
    pass


class DBModel(BaseModel):
    id: int | None = None

    @classmethod
    def create_table(cls) -> None:
        """Create a table in the database for the model."""
        columns = ["id INTEGER PRIMARY KEY"]
        for field_name, field_info in cls.model_fields.items():
            if field_name == "id":
                continue
            field_type = convert_to_sql_type(field_info.annotation)
            column_def = f"{field_name} {field_type}"
            if field_info.default not in (PydanticUndefined, None):
                column_def += f" DEFAULT '{field_info.default}'"
            if field_info.is_required():
                column_def += " NOT NULL"
            columns.append(column_def)

        sql = (
            f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} ({', '.join(columns)})"
        )
        cursor = execute_sql(sql)
        cursor.connection.close()

    def save(self) -> Self:
        """Save object to the database."""
        return self._update() if self.id else self._insert()

    @classmethod
    def _create_instance_from_data(cls, data):
        data_dict = dict(zip(cls.model_fields.keys(), data))
        for key, value in data_dict.items():
            annotation = cls.model_fields[key].annotation
            types_tuple = get_args(annotation)
            if (not types_tuple and annotation and issubclass(annotation, DBModel)) or (
                types_tuple and issubclass(types_tuple[0], DBModel)
            ):
                data_dict[key] = annotation.get(id=value)  # type: ignore
        return cls(**data_dict)

    @classmethod
    def get(cls, **kwargs) -> Self:
        """Get an object from the database based on the given keyword arguments."""
        conditions = " AND ".join(
            f"{field}='{value}'" for field, value in kwargs.items()
        )
        sql = f"SELECT * FROM {cls.__name__.lower()} WHERE {conditions}"
        cursor = execute_sql(sql)
        data = cursor.fetchone()
        cursor.connection.close()
        if data:
            return cls._create_instance_from_data(data)
        raise ObjectNotFound

    def delete(self) -> None:
        """Delete the object from the database."""
        cursor = execute_sql(
            f"DELETE FROM {self.__class__.__name__.lower()} WHERE id={self.id}"
        )
        cursor.connection.close()
        if cursor.rowcount == 0:
            raise ObjectNotFound

    def _insert(self) -> Self:
        model_dict = self.model_dump(exclude={"id"})
        fields = ", ".join(model_dict.keys())
        values = ", ".join(
            f"'{value.get('id')}'" if isinstance(value, dict) else f"'{value}'"
            for value in model_dict.values()
        )
        sql = f"INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({values})"
        cursor = execute_sql(sql)
        cursor.connection.close()
        self.id = cursor.lastrowid
        return self

    def _update(self) -> Self:
        model_dict = self.model_dump(exclude={"id"})
        fields = ", ".join(
            f"{field}='{value.get('id')}'"
            if isinstance(value, dict)
            else f"{field}='{value}'"
            for field, value in model_dict.items()
        )
        cursor = execute_sql(
            f"UPDATE {self.__class__.__name__.lower()} SET {fields} WHERE id={self.id}"
        )
        cursor.connection.close()
        if cursor.rowcount == 0:
            raise ObjectNotFound
        return self
