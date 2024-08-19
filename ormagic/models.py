from sqlite3 import Cursor
from typing import Any, Self

from pydantic import BaseModel

from ormagic import DBField

from . import table_manager
from .field_utils import (
    is_many_to_many_field,
    is_primary_key_field,
    prepare_where_conditions,
)
from .sql_utils import execute_sql


class ObjectNotFound(Exception):
    pass


class DBModel(BaseModel):
    id: int | None = DBField(primary_key=True)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        for field_name, field_info in cls.model_fields.items():
            if is_primary_key_field(field_info) and field_name != "id":
                cls.model_fields.pop("id")
                break

    @classmethod
    def create_table(cls) -> None:
        """Create a table in the database for the model."""
        table_manager.create_table(
            cls._get_table_name(), cls._get_primary_key_field_name(), cls.model_fields
        )

    @classmethod
    def update_table(cls) -> None:
        """Update the table in the database based on the model definition."""
        table_manager.update_table(
            cls._get_table_name(), cls._get_primary_key_field_name(), cls.model_fields
        )

    @classmethod
    def drop_table(cls) -> None:
        """Remove the table from the database."""
        table_manager.drop_table(cls._get_table_name())

    def save(self) -> Self:
        """Save object to the database."""
        return self._update() if self.is_object_exists() else self._insert()

    @classmethod
    def get(cls, *args, **kwargs) -> Self:
        """Get an object from the database based on the given keyword arguments."""
        return cls(**cls._fetchone_raw_data(*args, **kwargs))

    @classmethod
    def filter(cls, *args, **kwargs) -> list[Self]:
        """Get objects from the database based on the given keyword arguments."""
        return [cls(**data) for data in cls._fetchall_raw_data(*args, **kwargs)]

    @classmethod
    def all(cls, *args, **kwargs) -> list[Self]:
        """Get all objects from the database."""
        return [cls(**data) for data in cls._fetchall_raw_data(*args, **kwargs)]

    def delete(self) -> None:
        """Delete the object from the database."""
        cursor = execute_sql(
            f"DELETE FROM {self._get_table_name()} WHERE {self._get_primary_key_field_name()}={self.model_id}"
        )
        cursor.connection.close()
        if cursor.rowcount == 0:
            raise ObjectNotFound

    def _insert(self) -> Self:
        prepared_data = self._prepare_data_to_insert()
        fields = ", ".join(prepared_data.keys())
        values = ", ".join(
            f"'{value}'" if value else "NULL" for value in prepared_data.values()
        )
        sql = f"INSERT INTO {self._get_table_name()} ({fields}) VALUES ({values})"
        cursor = execute_sql(sql)
        cursor.connection.close()
        setattr(self, self._get_primary_key_field_name(), cursor.lastrowid)
        self._update_many_to_many_intermediate_table()
        return self

    def _update(self) -> Self:
        prepared_data = self._prepare_data_to_insert()
        prepared_data.pop(self._get_primary_key_field_name())
        fields = ", ".join(
            f"{field}='{value}'" if value else f"{field}=NULL"
            for field, value in prepared_data.items()
        )
        cursor = execute_sql(
            f"UPDATE {self._get_table_name()} SET {fields} WHERE {self._get_primary_key_field_name()}={self.model_id}"
        )
        cursor.connection.close()
        self._update_many_to_many_intermediate_table()
        return self

    def _update_many_to_many_intermediate_table(self) -> None:
        related_objects = []
        for field_name, field_info in self.model_fields.items():
            if is_many_to_many_field(field_info.annotation):
                related_objects.extend(iter(getattr(self, field_name)))
        if not related_objects:
            return
        table_name = self._get_table_name()
        related_table_name = related_objects[0].__class__.__name__.lower()
        intermediate_table_name = table_manager._get_intermediate_table_name(
            table_name, related_table_name
        )
        cursor = execute_sql(
            f"DELETE FROM {intermediate_table_name} WHERE {table_name}_id={self.model_id}"
        )
        for related_object in related_objects:
            if not related_object.model_id:
                related_object = related_object.save()
            cursor = execute_sql(
                f"INSERT INTO {intermediate_table_name} ({table_name}_id, {related_table_name}_id) VALUES ({self.model_id}, {related_object.model_id})"
            )
            cursor.connection.close()

    def _prepare_data_to_insert(self) -> dict[str, Any]:
        prepared_data = {}
        model_dict = self.model_dump()
        for field_name, field_info in self.model_fields.items():
            field_value = model_dict.get(field_name)
            if foreign_model := table_manager.get_foreign_key_model(
                field_info.annotation
            ):
                if isinstance(field_value, list):
                    continue
                elif not field_value:
                    prepared_data[field_name] = None
                elif not field_value[self._get_primary_key_field_name()]:
                    foreign_model = foreign_model(**field_value).save()
                    prepared_data[field_name] = foreign_model.model_id
                    # getattr(self, field_name).id = foreign_model.model_id
                    setattr(
                        getattr(self, field_name),
                        foreign_model._get_primary_key_field_name(),
                        foreign_model.model_id,
                    )
                else:
                    prepared_data[field_name] = field_value[
                        self._get_primary_key_field_name()
                    ]
            elif field_name == self._get_primary_key_field_name() and not field_value:
                continue
            else:
                prepared_data[field_name] = field_value
        return prepared_data

    def is_object_exists(self) -> bool:
        if not self.model_id:
            return False
        return bool(
            execute_sql(
                f"SELECT * FROM {self._get_table_name()} WHERE {self._get_primary_key_field_name()}={self.model_id}"
            ).fetchone()
        )

    @classmethod
    def _prepare_order_by(
        cls, order_by: str | list[str] | tuple[str] | set[str]
    ) -> str:
        if isinstance(order_by, (list, tuple, set)):
            return ", ".join(cls._prepare_order_by(field) for field in order_by)
        return f"{order_by[1:]} DESC" if order_by.startswith("-") else order_by

    @classmethod
    def _fetch_raw_data(cls, *args, **kwargs) -> Cursor:
        sql = f"SELECT * FROM {cls._get_table_name()}"
        where_conditions, where_params = prepare_where_conditions(*args, **kwargs)
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
        table_name = cls._get_table_name()
        related_model = getattr(annotation, "__args__")[0]
        related_table_name = related_model.__name__.lower()
        intermediate_table_name = table_manager._get_intermediate_table_name(
            table_name, related_table_name
        )
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
            if is_many_to_many_field(field_info.annotation):
                if is_recursive_call:
                    continue
                data_dict[key] = cls._process_many_to_many_data(
                    field_info.annotation, data_dict["id"]
                )
            elif not data_dict[key]:
                continue
            elif foreign_model := table_manager.get_foreign_key_model(
                field_info.annotation
            ):
                data_dict[key] = foreign_model._fetchone_raw_data(
                    model_id=data_dict[key]
                )
        return data_dict

    @classmethod
    def _fetchone_raw_data(
        cls,
        is_recursive_call: bool = False,
        model_id: int | None = None,
        *args,
        **kwargs,
    ) -> dict[str, Any]:
        if model_id:
            kwargs[cls._get_primary_key_field_name()] = model_id
        cursor = cls._fetch_raw_data(*args, **kwargs)
        data = cursor.fetchone()
        cursor.connection.close()
        if not data:
            raise ObjectNotFound
        return cls._process_raw_data(data, is_recursive_call)

    @classmethod
    def _fetchall_raw_data(cls, *args, **kwargs) -> list[dict[str, Any]]:
        cursor = cls._fetch_raw_data(*args, **kwargs)
        data_list = cursor.fetchall()
        cursor.connection.close()
        return [cls._process_raw_data(data) for data in data_list]

    @classmethod
    def _get_table_name(cls) -> str:
        return cls.__name__.lower()

    @property
    def model_id(self) -> int | None:
        return getattr(self, self._get_primary_key_field_name())

    @classmethod
    def _get_primary_key_field_name(cls) -> str:
        return next(
            (
                field_name
                for field_name, field_info in cls.model_fields.items()
                if is_primary_key_field(field_info)
            ),
            "",
        )
