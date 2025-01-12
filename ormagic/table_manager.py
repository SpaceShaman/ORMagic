from typing import TYPE_CHECKING, Any, Type, get_args

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from ormagic.field_utils import (
    get_on_delete_action,
    is_primary_key_field,
    is_unique_field,
    transform_field_annotation_to_sql_type,
)

from .clients.client import Client
from .field_utils import (
    is_many_to_many_field,
)

if TYPE_CHECKING:  # pragma: no cover
    from .models import DBModel


class UpdateTableError(Exception):
    pass


def create_table(
    client: Client,
    table_name: str,
    primary_key: str,
    model_fields: dict[str, FieldInfo],
):
    columns = []
    related_tables = []
    for field_name, field_info in model_fields.items():
        if is_many_to_many_field(field_info.annotation):
            related_tables.append(getattr(field_info.annotation, "__args__")[0])
            continue
        columns.append(prepare_column_definition(field_name, field_info))
    client.create_table(table_name, columns)
    for related_table in related_tables:
        _create_intermediate_table(client, table_name, primary_key, related_table)


def update_table(
    client: Client,
    table_name: str,
    primary_key: str,
    model_fields: dict[str, FieldInfo],
) -> None:
    if not client.is_table_exists(table_name):
        return create_table(client, table_name, primary_key, model_fields)
    if _some_fields_is_unique(model_fields):
        raise UpdateTableError("Cannot add unique field to existing table")
    existing_columns = client.get_column_names(table_name)
    new_columns = _get_model_field_names(model_fields)
    if existing_columns == new_columns:
        return
    elif len(existing_columns) > len(new_columns):
        _drop_columns_from_existing_table(
            client, table_name, existing_columns, new_columns
        )
    elif len(existing_columns) == len(new_columns):
        return _rename_columns_in_existing_table(
            client, table_name, existing_columns, new_columns
        )
    _add_new_columns_to_existing_table(
        client, table_name, model_fields, existing_columns
    )


def _some_fields_is_unique(model_fields: dict[str, FieldInfo]) -> bool:
    return any(is_unique_field(field_info) for field_info in model_fields.values())


def _create_intermediate_table(
    client: Client,
    table_name: str,
    primary_key: str,
    related_table: "DBModel",
) -> None:
    related_table_name = related_table._get_table_name()
    related_primary_key = related_table._get_primary_key_field_name()
    if not client.is_table_exists(related_table_name):
        return
    client.create_table(
        f"{table_name}_{related_table_name}",
        [
            "id INTEGER PRIMARY KEY",
            f"{table_name}_id INTEGER",
            f"{related_table_name}_id INTEGER",
            f"FOREIGN KEY ({table_name}_id) REFERENCES {table_name}({primary_key}) ON DELETE CASCADE ON UPDATE CASCADE",
            f"FOREIGN KEY ({related_table_name}_id) REFERENCES {related_table_name}({related_primary_key}) ON DELETE CASCADE ON UPDATE CASCADE",
        ],
    )


def get_intermediate_table_name(
    client: Client, table_name: str, related_table_name: str
) -> str:
    if client.is_table_exists(f"{table_name}_{related_table_name}"):
        return f"{table_name}_{related_table_name}"
    else:
        return f"{related_table_name}_{table_name}"


def prepare_column_definition(field_name: str, field_info: FieldInfo) -> str:
    field_type = transform_field_annotation_to_sql_type(field_info.annotation)
    column_definition = f"{field_name} {field_type}"
    if field_info.default not in (PydanticUndefined, None):
        column_definition += f" DEFAULT '{field_info.default}'"
    if field_info.is_required():
        column_definition += " NOT NULL"
    if is_unique_field(field_info):
        column_definition += " UNIQUE"
    if foreign_model := get_foreign_key_model(field_info.annotation):
        action = get_on_delete_action(field_info)
        column_definition += f", FOREIGN KEY ({field_name}) REFERENCES {foreign_model._get_table_name()}({foreign_model._get_primary_key_field_name()}) ON UPDATE {action} ON DELETE {action}"
    if is_primary_key_field(field_info):
        column_definition += " PRIMARY KEY"
    return column_definition


def get_foreign_key_model(field_annotation: Any) -> Type | None:
    from .models import DBModel

    types_tuple = get_args(field_annotation)
    if not types_tuple and field_annotation and issubclass(field_annotation, DBModel):
        return field_annotation
    if types_tuple and issubclass(types_tuple[0], DBModel):
        return types_tuple[0]


def _get_model_field_names(model_fields: dict[str, FieldInfo]) -> list[str]:
    return list(model_fields.keys())


def _rename_columns_in_existing_table(
    client: Client, table_name: str, old_columns: list[str], new_columns: list[str]
) -> None:
    for old_column_name, new_column_name in dict(zip(old_columns, new_columns)).items():
        if old_column_name != new_column_name:
            client.rename_column(table_name, old_column_name, new_column_name)


def _add_new_columns_to_existing_table(
    client: Client,
    table_name: str,
    model_fields: dict[str, FieldInfo],
    existing_columns: list[str],
) -> None:
    for field_name, field_info in model_fields.items():
        if field_name in existing_columns:
            continue
        column_definition = prepare_column_definition(field_name, field_info)
        client.add_column(table_name, column_definition)


def _drop_columns_from_existing_table(
    client: Client, table_name: str, existing_columns: list[str], new_columns: list[str]
) -> None:
    columns_to_drop = set(existing_columns) - set(new_columns)
    for column_name in columns_to_drop:
        client.drop_column(table_name, column_name)
