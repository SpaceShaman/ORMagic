from sqlite3 import Cursor
from typing import Any, Literal, Self, Type, get_args

from pydantic import BaseModel
from pydantic.fields import FieldInfo
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
            table_name = cls.__name__.lower()
            if cls._is_many_to_many_field(field_info.annotation):
                cls._create_intermediate_table(field_info)
                continue
            field_type = convert_to_sql_type(field_info.annotation)
            column_def = f"{field_name} {field_type}"
            if field_info.default not in (PydanticUndefined, None):
                column_def += f" DEFAULT '{field_info.default}'"
            if field_info.is_required():
                column_def += " NOT NULL"
            if field_info.json_schema_extra and field_info.json_schema_extra.get(
                "unique"
            ):
                column_def += " UNIQUE"
            if foreign_model := cls._get_foreign_key_model(field_name):
                action = cls._get_on_delete_action(field_info)
                column_def += f", FOREIGN KEY ({field_name}) REFERENCES {foreign_model.__name__.lower()}(id) ON UPDATE {action} ON DELETE {action}"
            columns.append(column_def)

        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        cursor = execute_sql(sql)
        cursor.connection.close()

    @classmethod
    def drop_table(cls) -> None:
        """Remove the table from the database."""
        cursor = execute_sql(f"DROP TABLE IF EXISTS {cls.__name__.lower()}")
        cursor.connection.close()

    def save(self) -> Self:
        """Save object to the database."""
        return self._update() if self.id else self._insert()

    @classmethod
    def get(cls, **kwargs) -> Self:
        """Get an object from the database based on the given keyword arguments."""
        return cls(**cls._fetchone_raw_data(**kwargs))

    @classmethod
    def filter(cls, **kwargs) -> list[Self]:
        """Get objects from the database based on the given keyword arguments."""
        return [cls(**data) for data in cls._fetchall_raw_data(**kwargs)]

    @classmethod
    def all(cls) -> list[Self]:
        """Get all objects from the database."""
        return [cls(**data) for data in cls._fetchall_raw_data()]

    def delete(self) -> None:
        """Delete the object from the database."""
        cursor = execute_sql(f"DELETE FROM {self.table_name} WHERE id={self.id}")
        cursor.connection.close()
        if cursor.rowcount == 0:
            raise ObjectNotFound

    def _insert(self) -> Self:
        prepared_data = self._prepare_data_to_insert(self.model_dump(exclude={"id"}))
        fields = ", ".join(prepared_data.keys())
        values = ", ".join(
            f"'{value}'" if value else "NULL" for value in prepared_data.values()
        )
        sql = f"INSERT INTO {self.table_name} ({fields}) VALUES ({values})"
        cursor = execute_sql(sql)
        cursor.connection.close()
        self.id = cursor.lastrowid
        self._update_many_to_many_intermediate_table()
        return self

    def _update(self) -> Self:
        prepared_data = self._prepare_data_to_insert(self.model_dump(exclude={"id"}))
        fields = ", ".join(
            f"{field}='{value}'" if value else f"{field}=NULL"
            for field, value in prepared_data.items()
        )
        cursor = execute_sql(
            f"UPDATE {self.table_name} SET {fields} WHERE id={self.id}"
        )
        cursor.connection.close()
        if cursor.rowcount == 0:
            raise ObjectNotFound
        self._update_many_to_many_intermediate_table()
        return self

    def _update_many_to_many_intermediate_table(self) -> None:
        related_objects = []
        for field_name, field_info in self.model_fields.items():
            if self._is_many_to_many_field(field_info.annotation):
                related_objects.extend(iter(getattr(self, field_name)))
        if not related_objects:
            return
        related_table_name = related_objects[0].__class__.__name__.lower()
        intermediate_table_name = self._get_intermediate_table_name(related_table_name)
        cursor = execute_sql(
            f"DELETE FROM {intermediate_table_name} WHERE {self.table_name}_id={self.id}"
        )
        for related_object in related_objects:
            if not related_object.id:
                related_object = related_object.save()
            cursor = execute_sql(
                f"INSERT INTO {intermediate_table_name} ({self.table_name}_id, {related_table_name}_id) VALUES ({self.id}, {related_object.id})"
            )
            cursor.connection.close()

    def _prepare_data_to_insert(self, model_dict: dict) -> dict[str, Any]:
        prepared_data = {}
        for key, value in model_dict.items():
            if foreign_model := self._get_foreign_key_model(key):
                if isinstance(value, list):
                    continue
                elif not value:
                    prepared_data[key] = None
                elif not value["id"]:
                    value = foreign_model(**value).save()
                    prepared_data[key] = value.id
                    getattr(self, key).id = value.id
                else:
                    prepared_data[key] = value["id"]
            else:
                prepared_data[key] = value
        return prepared_data

    @classmethod
    def _get_foreign_key_model(cls, field_name: str) -> Type["DBModel"] | None:
        annotation = cls.model_fields[field_name].annotation
        types_tuple = get_args(annotation)
        if not types_tuple and annotation and issubclass(annotation, DBModel):
            return annotation
        if types_tuple and issubclass(types_tuple[0], DBModel):
            return types_tuple[0]

    @classmethod
    def _get_on_delete_action(
        cls, field_info: FieldInfo
    ) -> Literal["CASCADE", "SET NULL", "RESTRICT", "SET DEFAULT", "NO ACTION"]:
        if not field_info.json_schema_extra:
            return "CASCADE"
        if field_info.json_schema_extra.get("on_delete") == "SET NULL":
            return "SET NULL"
        if field_info.json_schema_extra.get("on_delete") == "RESTRICT":
            return "RESTRICT"
        if field_info.json_schema_extra.get("on_delete") == "SET DEFAULT":
            return "SET DEFAULT"
        if field_info.json_schema_extra.get("on_delete") == "NO ACTION":
            return "NO ACTION"
        return "CASCADE"

    @classmethod
    def _fetch_raw_data(cls, **kwargs) -> Cursor:
        conditions = " AND ".join(
            f"{field}='{value}'" for field, value in kwargs.items()
        )
        sql = f"SELECT * FROM {cls.__name__.lower()}"
        if conditions:
            sql += f" WHERE {conditions}"
        return execute_sql(sql)

    @classmethod
    def _process_many_to_many_data(
        cls, annotation: Any, object_id: int
    ) -> list[dict[str, Any]]:
        table_name = cls.__name__.lower()
        related_model = getattr(annotation, "__args__")[0]
        related_table_name = related_model.__name__.lower()
        intermediate_table_name = cls._get_intermediate_table_name(related_table_name)
        cursor = execute_sql(
            f"SELECT {related_table_name}_id FROM {intermediate_table_name} WHERE {table_name}_id={object_id}"
        )
        return [
            related_model._fetchone_raw_data(id=row[0], is_recursive_call=True)
            for row in cursor.fetchall()
        ]

    @classmethod
    def _process_raw_data(
        cls, data: tuple, is_recursive_call: bool = False
    ) -> dict[str, Any]:
        data_dict = dict(zip(cls.model_fields.keys(), data))
        for key, field_info in cls.model_fields.items():
            if cls._is_many_to_many_field(field_info.annotation):
                if is_recursive_call:
                    continue
                data_dict[key] = cls._process_many_to_many_data(
                    field_info.annotation, data_dict["id"]
                )
            elif not data_dict[key]:
                continue
            elif foreign_model := cls._get_foreign_key_model(key):
                data_dict[key] = foreign_model._fetchone_raw_data(id=data_dict[key])
        return data_dict

    @classmethod
    def _fetchone_raw_data(
        cls, is_recursive_call: bool = False, **kwargs
    ) -> dict[str, Any]:
        cursor = cls._fetch_raw_data(**kwargs)
        data = cursor.fetchone()
        cursor.connection.close()
        if not data:
            raise ObjectNotFound
        return cls._process_raw_data(data, is_recursive_call)

    @classmethod
    def _fetchall_raw_data(cls, **kwargs) -> list[dict[str, Any]]:
        cursor = cls._fetch_raw_data(**kwargs)
        data_list = cursor.fetchall()
        cursor.connection.close()
        return [cls._process_raw_data(data) for data in data_list]

    @classmethod
    def _is_many_to_many_field(cls, annotation: Any) -> bool:
        return bool(
            hasattr(annotation, "__origin__")
            and getattr(annotation, "__origin__") is list
            and issubclass(getattr(annotation, "__args__")[0], DBModel)
        )

    @classmethod
    def _create_intermediate_table(cls, field_info: FieldInfo) -> None:
        table_name = cls.__name__.lower()
        related_table_name = getattr(field_info.annotation, "__args__")[
            0
        ].__name__.lower()
        if cls._get_intermediate_table_name(related_table_name):
            return
        execute_sql(
            f"CREATE TABLE IF NOT EXISTS {table_name}_{related_table_name} ("
            "id INTEGER PRIMARY KEY, "
            f"{table_name}_id INTEGER, "
            f"{related_table_name}_id INTEGER, "
            f"FOREIGN KEY ({table_name}_id) REFERENCES {table_name}(id) ON DELETE CASCADE, "
            f"FOREIGN KEY ({related_table_name}_id) REFERENCES {related_table_name}(id) ON DELETE CASCADE)"
        )

    @classmethod
    def _get_intermediate_table_name(cls, related_table_name: str) -> str | None:
        table_name = cls.__name__.lower()
        cursor = execute_sql(
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}_{related_table_name}'"
        )
        if cursor.fetchone()[0] == 1:
            return f"{table_name}_{related_table_name}"
        cursor = execute_sql(
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{related_table_name}_{table_name}'"
        )
        if cursor.fetchone()[0] == 1:
            return f"{related_table_name}_{table_name}"
        return None

    @property
    def table_name(self) -> str:
        return self.__class__.__name__.lower()
