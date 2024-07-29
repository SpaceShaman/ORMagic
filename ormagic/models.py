from typing import Any, Iterable, Literal, Self, Type, get_args

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
        if data := cls._fetch_raw_data(fetchall=False, **kwargs):
            return cls._create_instance_from_data(data)
        raise ObjectNotFound

    @classmethod
    def filter(cls, **kwargs) -> list[Self]:
        """Get objects from the database based on the given keyword arguments."""
        return [
            cls._create_instance_from_data(row)
            for row in cls._fetch_raw_data(fetchall=True, **kwargs)
        ]

    @classmethod
    def all(cls) -> list[Self]:
        """Get all objects from the database."""
        return [
            cls._create_instance_from_data(row)
            for row in cls._fetch_raw_data(fetchall=True)
        ]

    def delete(self) -> None:
        """Delete the object from the database."""
        cursor = execute_sql(
            f"DELETE FROM {self.__class__.__name__.lower()} WHERE id={self.id}"
        )
        cursor.connection.close()
        if cursor.rowcount == 0:
            raise ObjectNotFound

    def _insert(self) -> Self:
        intermidiate_fields = [
            field_name
            for field_name, field_info in self.model_fields.items()
            if self._is_many_to_many_field(field_info.annotation)
        ]
        model_dict = self.model_dump(exclude={"id", *intermidiate_fields})

        prepared_data = self._prepare_values_to_insert(model_dict)
        fields = ", ".join(prepared_data.keys())
        values = ", ".join(f"'{value}'" for value in prepared_data.values())
        sql = f"INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({values})"
        cursor = execute_sql(sql)
        cursor.connection.close()
        self.id = cursor.lastrowid
        for field_name in intermidiate_fields:
            related_table_name = getattr(
                self.__class__.model_fields[field_name].annotation, "__args__"
            )[0].__name__.lower()
            intermediate_table_name = self._get_intermediate_table_name(
                related_table_name
            )
            related_objects = getattr(self, field_name)
            for related_object in related_objects:
                execute_sql(
                    f"INSERT INTO {intermediate_table_name} ({self.__class__.__name__.lower()}_id, {related_table_name}_id) VALUES ({self.id}, {related_object.id})"
                )
        return self

    def _update(self) -> Self:
        model_dict = self.model_dump(exclude={"id"})
        prepared_data = self._prepare_values_to_insert(model_dict)
        fields = ", ".join(
            f"{field}='{value}'" for field, value in prepared_data.items()
        )
        cursor = execute_sql(
            f"UPDATE {self.__class__.__name__.lower()} SET {fields} WHERE id={self.id}"
        )
        cursor.connection.close()
        if cursor.rowcount == 0:
            raise ObjectNotFound
        return self

    @classmethod
    def _create_instance_from_data(cls, data: Iterable) -> Self:
        data_dict = dict(zip(cls.model_fields.keys(), data))
        for key, value in data_dict.items():
            if not value:
                data_dict[key] = None
            elif foreign_model := cls._get_foreign_key_model(key):
                data_dict[key] = foreign_model.get(id=value)
        return cls(**data_dict)

    def _prepare_values_to_insert(self, model_dict: dict) -> dict[str, Any]:
        values = {}
        for key, value in model_dict.items():
            if foreign_model := self._get_foreign_key_model(key):
                if not value:
                    continue
                if not value["id"]:
                    value = foreign_model(**value).save()
                    values[key] = value.id
                    getattr(self, key).id = value.id
                else:
                    values[key] = value["id"]
            elif not value:
                values[key] = None
            else:
                values[key] = value
        return values

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
    def _fetch_raw_data(cls, fetchall: bool, **kwargs) -> list[tuple[Any]] | tuple[Any]:
        conditions = " AND ".join(
            f"{field}='{value}'" for field, value in kwargs.items()
        )
        sql = f"SELECT * FROM {cls.__name__.lower()}"
        if conditions:
            sql += f" WHERE {conditions}"
        cursor = execute_sql(sql)
        data: tuple | list[tuple] = cursor.fetchall() if fetchall else cursor.fetchone()
        cursor.connection.close()
        return data

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
        # Check if the intermediate table already exists
        if cls._get_intermediate_table_name(related_table_name):
            return
        # Create the intermediate table if it doesn't exist for many-to-many relationships
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
