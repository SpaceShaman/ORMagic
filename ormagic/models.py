from sqlite3 import Cursor
from types import NoneType
from typing import Any, Literal, Self, Type, Union, get_args

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .sql_utils import execute_sql


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
            if cls._is_many_to_many_field(field_info.annotation):
                cls._create_intermediate_table(field_info)
                continue
            columns.append(cls._prepare_column_definition(field_name, field_info))

        sql = (
            f"CREATE TABLE IF NOT EXISTS {cls._get_table_name()} ({', '.join(columns)})"
        )
        cursor = execute_sql(sql)
        cursor.connection.close()

    @classmethod
    def update_table(cls) -> None:
        """Update the table in the database based on the model definition."""
        if not cls._is_table_exists():
            return cls.create_table()
        existing_columns = cls._fetch_existing_column_names_from_db()
        model_fields = cls._fetch_field_names_from_model()
        if existing_columns == model_fields:
            return
        elif len(existing_columns) == len(model_fields):
            return cls._rename_columns(existing_columns, model_fields)
        cls._add_new_columns_to_existing_table(existing_columns)

    @classmethod
    def drop_table(cls) -> None:
        """Remove the table from the database."""
        cursor = execute_sql(f"DROP TABLE IF EXISTS {cls._get_table_name()}")
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
    def all(cls, **kwargs) -> list[Self]:
        """Get all objects from the database."""
        return [cls(**data) for data in cls._fetchall_raw_data(**kwargs)]

    def delete(self) -> None:
        """Delete the object from the database."""
        cursor = execute_sql(f"DELETE FROM {self._get_table_name()} WHERE id={self.id}")
        cursor.connection.close()
        if cursor.rowcount == 0:
            raise ObjectNotFound

    @classmethod
    def _fetch_existing_column_names_from_db(cls) -> list[str]:
        cursor = execute_sql(f"PRAGMA table_info({cls._get_table_name()})")
        existed_fields = [column[1] for column in cursor.fetchall()]
        cursor.connection.close()
        return existed_fields

    @classmethod
    def _fetch_field_names_from_model(cls) -> list[str]:
        return list(cls.model_fields.keys())

    @classmethod
    def _rename_columns(cls, old_columns: list[str], new_columns: list[str]) -> None:
        for old_column_name, new_column_name in dict(
            zip(old_columns, new_columns)
        ).items():
            cursor = execute_sql(
                f"ALTER TABLE {cls._get_table_name()} RENAME COLUMN {old_column_name} TO {new_column_name}"
            )
            cursor.connection.close()

    @classmethod
    def _add_new_columns_to_existing_table(cls, existing_columns: list[str]) -> None:
        for field_name, field_info in cls.model_fields.items():
            if field_name in existing_columns:
                continue
            column_definition = cls._prepare_column_definition(field_name, field_info)
            cursor = execute_sql(
                f"ALTER TABLE {cls._get_table_name()} ADD COLUMN {column_definition}"
            )
            cursor.connection.close()

    @classmethod
    def _prepare_column_definition(cls, field_name: str, field_info: FieldInfo) -> str:
        field_type = cls._transform_field_annotation_to_sql_type(field_info.annotation)
        column_definition = f"{field_name} {field_type}"
        if field_info.default not in (PydanticUndefined, None):
            column_definition += f" DEFAULT '{field_info.default}'"
        if field_info.is_required():
            column_definition += " NOT NULL"
        if cls._is_unique_field(field_info):
            column_definition += " UNIQUE"
        if foreign_model := cls._get_foreign_key_model(field_name):
            action = cls._get_on_delete_action(field_info)
            column_definition += f", FOREIGN KEY ({field_name}) REFERENCES {foreign_model.__name__.lower()}(id) ON UPDATE {action} ON DELETE {action}"
        return column_definition

    def _insert(self) -> Self:
        prepared_data = self._prepare_data_to_insert(self.model_dump(exclude={"id"}))
        fields = ", ".join(prepared_data.keys())
        values = ", ".join(
            f"'{value}'" if value else "NULL" for value in prepared_data.values()
        )
        sql = f"INSERT INTO {self._get_table_name()} ({fields}) VALUES ({values})"
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
            f"UPDATE {self._get_table_name()} SET {fields} WHERE id={self.id}"
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
        table_name = self._get_table_name()
        related_table_name = related_objects[0].__class__.__name__.lower()
        intermediate_table_name = self._get_intermediate_table_name(related_table_name)
        cursor = execute_sql(
            f"DELETE FROM {intermediate_table_name} WHERE {table_name}_id={self.id}"
        )
        for related_object in related_objects:
            if not related_object.id:
                related_object = related_object.save()
            cursor = execute_sql(
                f"INSERT INTO {intermediate_table_name} ({table_name}_id, {related_table_name}_id) VALUES ({self.id}, {related_object.id})"
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
    def _transform_field_annotation_to_sql_type(
        cls, annotation: Any
    ) -> Literal["INTEGER", "TEXT"]:
        if annotation in [int, Union[int, NoneType]]:
            return "INTEGER"
        types_tuple = get_args(annotation)
        if not types_tuple and issubclass(annotation, DBModel):
            return "INTEGER"
        if types_tuple and issubclass(types_tuple[0], DBModel):
            return "INTEGER"
        return "TEXT"

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
    def _extract_field_operator(cls, field: str) -> tuple[str, str]:
        if "__" not in field:
            return field, "="
        field, operator = field.split("__")
        if operator == "ne":
            operator = "<>"
        elif operator == "gt":
            operator = ">"
        elif operator == "gte":
            operator = ">="
        elif operator == "lt":
            operator = "<"
        elif operator == "lte":
            operator = "<="
        elif operator == "like":
            operator = " LIKE "
        elif operator == "nlike":
            operator = " NOT LIKE "
        elif operator == "in":
            operator = " IN "
        elif operator == "nin":
            operator = " NOT IN "
        elif operator == "between":
            operator = " BETWEEN "
        elif operator == "nbetween":
            operator = " NOT BETWEEN "
        else:
            raise ValueError(f"Invalid operator: {operator}")
        return field, operator

    @classmethod
    def _prepare_where_conditions(cls, **kwargs) -> tuple[str, list]:
        conditions = []
        params = []
        for field, value in kwargs.items():
            if field in ("order_by", "limit", "offset"):
                continue
            field, operator = cls._extract_field_operator(field)
            if not cls.model_fields.get(field):
                raise ValueError(f"Invalid field: {field}")
            if "IN" in operator:
                placeholders = ", ".join(["?"] * len(value))
                conditions.append(f"{field} {operator} ({placeholders})")
                params.extend(value)
            elif "BETWEEN" in operator:
                conditions.append(f"{field} {operator} ? AND ?")
                params.extend(value)
            else:
                conditions.append(f"{field} {operator} ?")
                params.append(value)
        return " AND ".join(conditions), params

    @classmethod
    def _prepare_order_by(
        cls, order_by: str | list[str] | tuple[str] | set[str]
    ) -> str:
        if isinstance(order_by, (list, tuple, set)):
            return ", ".join(cls._prepare_order_by(field) for field in order_by)
        return f"{order_by[1:]} DESC" if order_by.startswith("-") else order_by

    @classmethod
    def _fetch_raw_data(cls, **kwargs) -> Cursor:
        sql = f"SELECT * FROM {cls._get_table_name()}"
        where_conditions, where_params = cls._prepare_where_conditions(**kwargs)
        if where_conditions:
            sql += f" WHERE {where_conditions}"
        if order_by := kwargs.get("order_by"):
            order_by = cls._prepare_order_by(order_by)
            sql += f" ORDER BY {order_by}"
        if limit := kwargs.get("limit"):
            sql += f" LIMIT {limit}"
        if offset := kwargs.get("offset"):
            sql += f" OFFSET {offset}"
        return execute_sql(sql, where_params)

    @classmethod
    def _process_many_to_many_data(
        cls, annotation: Any, object_id: int
    ) -> list[dict[str, Any]]:
        related_model = getattr(annotation, "__args__")[0]
        related_table_name = related_model.__name__.lower()
        intermediate_table_name = cls._get_intermediate_table_name(related_table_name)
        cursor = execute_sql(
            f"SELECT {related_table_name}_id FROM {intermediate_table_name} WHERE {cls._get_table_name()}_id={object_id}"
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
    def _is_unique_field(cls, field_info: FieldInfo) -> bool:
        return bool(
            field_info.json_schema_extra and field_info.json_schema_extra.get("unique")
        )

    @classmethod
    def _is_table_exists(cls) -> bool:
        cursor = execute_sql(
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{cls._get_table_name()}'"
        )
        exist = cursor.fetchone()[0] == 1
        cursor.connection.close()
        return exist

    @classmethod
    def _create_intermediate_table(cls, field_info: FieldInfo) -> None:
        table_name = cls._get_table_name()
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
    def _get_table_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def _get_intermediate_table_name(cls, related_table_name: str) -> str | None:
        table_name = cls._get_table_name()
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
