from typing import Any, Self

from pydantic import BaseModel

from ormagic import DBField

from .clients.client import Client, client_context
from .field_utils import (
    is_many_to_many_field,
    is_primary_key_field,
    prepare_where_conditions,
)
from .table_manager import (
    create_table,
    get_foreign_key_model,
    get_intermediate_table_name,
    update_table,
)


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
        with client_context() as client:
            create_table(
                client,
                cls._get_table_name(),
                cls._get_primary_key_field_name(),
                cls.model_fields,
            )

    @classmethod
    def update_table(cls) -> None:
        """Update the table in the database based on the model definition."""
        with client_context() as client:
            update_table(
                client,
                cls._get_table_name(),
                cls._get_primary_key_field_name(),
                cls.model_fields,
            )

    @classmethod
    def drop_table(cls) -> None:
        """Remove the table from the database."""
        with client_context() as client:
            client.drop_table(cls._get_table_name())

    def save(self) -> Self:
        """Save object to the database."""
        with client_context() as client:
            return (
                self._update(client)
                if self.is_object_exists(client)
                else self._insert(client)
            )

    @classmethod
    def get(cls, *args, **kwargs) -> Self:
        """Get an object from the database based on the given keyword arguments."""
        with client_context() as client:
            return cls(**cls._fetchone_raw_data(client, *args, **kwargs))

    @classmethod
    def filter(cls, *args, **kwargs) -> list[Self]:
        """Get objects from the database based on the given keyword arguments."""
        with client_context() as client:
            return [
                cls(**data) for data in cls._fetchall_raw_data(client, *args, **kwargs)
            ]

    @classmethod
    def all(cls, *args, **kwargs) -> list[Self]:
        """Get all objects from the database."""
        with client_context() as client:
            return [
                cls(**data) for data in cls._fetchall_raw_data(client, *args, **kwargs)
            ]

    def delete(self) -> None:
        """Delete the object from the database."""
        with client_context() as client:
            client.delete_rows(
                self._get_table_name(),
                f"{self._get_primary_key_field_name()}={self.model_id}",
            )

    def _insert(self, client: Client) -> Self:
        prepared_data = self._prepare_data_to_insert()
        row_id = client.insert_row_and_get_id(
            self._get_table_name(),
            list(prepared_data.keys()),
            list(prepared_data.values()),
            self._get_primary_key_field_name(),
        )
        setattr(self, self._get_primary_key_field_name(), row_id)
        self._update_many_to_many_intermediate_table(client)
        return self

    def _update(self, client: Client) -> Self:
        data = self._prepare_data_to_insert()
        data.pop(self._get_primary_key_field_name())
        client.update_rows(
            self._get_table_name(),
            data,
            f"{self._get_primary_key_field_name()}={self.model_id}",
        )
        self._update_many_to_many_intermediate_table(client)
        return self

    def _update_many_to_many_intermediate_table(self, client: Client) -> None:
        related_objects = []
        for field_name, field_info in self.model_fields.items():
            if is_many_to_many_field(field_info.annotation):
                related_objects.extend(iter(getattr(self, field_name)))
        if not related_objects:
            return
        table_name = self._get_table_name()
        related_table_name = related_objects[0]._get_table_name()
        intermediate_table_name = get_intermediate_table_name(
            client, table_name, related_table_name
        )
        client.delete_rows(intermediate_table_name, f"{table_name}_id={self.model_id}")
        for related_object in related_objects:
            if not related_object.model_id:
                related_object = related_object.save()
            client.insert_row(
                intermediate_table_name,
                [f"{table_name}_id", f"{related_table_name}_id"],
                [str(self.model_id), str(related_object.model_id)],
            )

    def _prepare_data_to_insert(self) -> dict[str, Any]:
        prepared_data = {}
        model_dict = self.model_dump()
        for field_name, field_info in self.model_fields.items():
            field_value = model_dict.get(field_name)
            if foreign_model := get_foreign_key_model(field_info.annotation):
                if isinstance(field_value, list):
                    continue
                elif not field_value:
                    prepared_data[field_name] = None
                elif not field_value[self._get_primary_key_field_name()]:
                    foreign_model = foreign_model(**field_value).save()
                    prepared_data[field_name] = foreign_model.model_id
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

    def is_object_exists(self, client: Client) -> bool:
        if not self.model_id:
            return False
        return client.is_row_exists(
            self._get_table_name(),
            f"{self._get_primary_key_field_name()}={self.model_id}",
        )

    @classmethod
    def _prepare_order_by(
        cls, order_by: str | list[str] | tuple[str] | set[str]
    ) -> str:
        if isinstance(order_by, (list, tuple, set)):
            return ", ".join(cls._prepare_order_by(field) for field in order_by)
        return f"{order_by[1:]} DESC" if order_by.startswith("-") else order_by

    @classmethod
    def _prepare_query_to_fetch_raw_data(cls, *args, **kwargs) -> tuple[str, list]:
        sql = f"SELECT * FROM {cls._get_table_name()}"
        where_conditions, params = prepare_where_conditions(*args, **kwargs)
        if where_conditions:
            sql += f" WHERE {where_conditions}"
        if order_by := kwargs.get("order_by"):
            order_by = cls._prepare_order_by(order_by)
            sql += f" ORDER BY {order_by}"
        if limit := kwargs.get("limit"):
            sql += f" LIMIT {limit}"
        if offset := kwargs.get("offset"):
            sql += f" OFFSET {offset}"
        return sql, params

    @classmethod
    def _process_many_to_many_data(
        cls, client: Client, annotation: Any, object_id: int
    ) -> list[dict[str, Any]]:
        table_name = cls._get_table_name()
        related_model = getattr(annotation, "__args__")[0]
        related_table_name = related_model._get_table_name()
        intermediate_table_name = get_intermediate_table_name(
            client, table_name, related_table_name
        )
        rows = client.fetchall(
            f"SELECT {related_table_name}_id FROM {intermediate_table_name} WHERE {table_name}_id=?",
            [object_id],
        )
        return [
            related_model._fetchone_raw_data(
                client, is_recursive_call=True, model_id=row[0]
            )
            for row in rows
        ]

    @classmethod
    def _process_raw_data(
        cls, client: Client, data: tuple, is_recursive_call: bool = False
    ) -> dict[str, Any]:
        data_dict = dict(zip(cls.model_fields.keys(), data))
        for key, field_info in cls.model_fields.items():
            if is_many_to_many_field(field_info.annotation):
                if is_recursive_call:
                    continue
                data_dict[key] = cls._process_many_to_many_data(
                    client,
                    field_info.annotation,
                    data_dict[cls._get_primary_key_field_name()],
                )
            elif not data_dict[key]:
                continue
            elif foreign_model := get_foreign_key_model(field_info.annotation):
                data_dict[key] = foreign_model._fetchone_raw_data(
                    client, model_id=data_dict[key]
                )
        return data_dict

    @classmethod
    def _fetchone_raw_data(
        cls,
        client: Client,
        is_recursive_call: bool = False,
        model_id: int | None = None,
        *args,
        **kwargs,
    ) -> dict[str, Any]:
        if model_id:
            kwargs[cls._get_primary_key_field_name()] = model_id
        sql, params = cls._prepare_query_to_fetch_raw_data(*args, **kwargs)
        if data := client.fetchone(sql, params):
            return cls._process_raw_data(client, data, is_recursive_call)
        else:
            raise ObjectNotFound

    @classmethod
    def _fetchall_raw_data(
        cls, client: Client, *args, **kwargs
    ) -> list[dict[str, Any]]:
        query, params = cls._prepare_query_to_fetch_raw_data(*args, **kwargs)
        data_list = client.fetchall(query, params)
        return [cls._process_raw_data(client, data) for data in data_list]

    @classmethod
    def _get_table_name(cls) -> str:
        return f"{cls.__name__.lower()}s"

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
