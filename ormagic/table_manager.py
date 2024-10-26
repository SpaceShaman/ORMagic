from typing import Any, Type, get_args

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .connection import Cursor
from .field_utils import (
    get_on_delete_action,
    is_many_to_many_field,
    is_primary_key_field,
    is_unique_field,
    transform_field_annotation_to_sql_type,
)


def create_table(
    cursor: Cursor,
    table_name: str,
    primary_key: str,
    model_fields: dict[str, FieldInfo],
):
    columns = []
    for field_name, field_info in model_fields.items():
        if is_many_to_many_field(field_info.annotation):
            related_table = getattr(field_info.annotation, "__args__")[0]
            related_table_name = related_table._get_table_name()
            related_primary_key = related_table._get_primary_key_field_name()
            _create_intermediate_table(
                cursor, table_name, primary_key, related_table_name, related_primary_key
            )
            continue
        columns.append(_prepare_column_definition(field_name, field_info))
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")


def update_table(
    cursor: Cursor,
    table_name: str,
    primary_key: str,
    model_fields: dict[str, FieldInfo],
) -> None:
    if not _is_table_exists(cursor, table_name):
        return create_table(cursor, table_name, primary_key, model_fields)
    existing_columns = _fetch_existing_column_names_from_db(cursor, table_name)
    new_columns = _fetch_field_names_from_model(model_fields)
    if existing_columns == new_columns:
        return
    elif len(existing_columns) > len(new_columns):
        _drop_columns_from_existing_table(
            cursor, table_name, existing_columns, new_columns
        )
    elif len(existing_columns) == len(new_columns):
        return _rename_columns_in_existing_table(
            cursor, table_name, existing_columns, new_columns
        )
    _add_new_columns_to_existing_table(
        cursor, table_name, model_fields, existing_columns
    )


def get_foreign_key_model(field_annotation: Any) -> Type | None:
    from .models import DBModel

    types_tuple = get_args(field_annotation)
    if not types_tuple and field_annotation and issubclass(field_annotation, DBModel):
        return field_annotation
    if types_tuple and issubclass(types_tuple[0], DBModel):
        return types_tuple[0]


def _create_intermediate_table(
    cursor: Cursor,
    table_name: str,
    primary_key: str,
    related_table_name: str,
    related_primary_key: str,
) -> None:
    if get_intermediate_table_name(cursor, table_name, related_table_name):
        return
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name}_{related_table_name} ("
        "id INTEGER PRIMARY KEY, "
        f"{table_name}_id INTEGER, "
        f"{related_table_name}_id INTEGER, "
        f"FOREIGN KEY ({table_name}_id) REFERENCES {table_name}({primary_key}) ON DELETE CASCADE ON UPDATE CASCADE, "
        f"FOREIGN KEY ({related_table_name}_id) REFERENCES {related_table_name}({related_primary_key}) ON DELETE CASCADE ON UPDATE CASCADE) "
    )


def get_intermediate_table_name(
    cursor: Cursor, table_name: str, related_table_name: str
) -> str | None:
    cursor.execute(
        f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}_{related_table_name}'"
    )
    count = cursor.fetchone()[0]
    if count == 1:
        return f"{table_name}_{related_table_name}"
    cursor.execute(
        f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{related_table_name}_{table_name}'"
    )
    count = cursor.fetchone()[0]
    return f"{related_table_name}_{table_name}" if count == 1 else None


def _prepare_column_definition(field_name: str, field_info: FieldInfo) -> str:
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
        column_definition += f", FOREIGN KEY ({field_name}) REFERENCES {foreign_model.__name__.lower()}({foreign_model._get_primary_key_field_name()}) ON UPDATE {action} ON DELETE {action}"
    if is_primary_key_field(field_info):
        column_definition += " PRIMARY KEY"
    return column_definition


def _is_table_exists(cursor: Cursor, table_name: str) -> bool:
    cursor.execute(
        f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    return cursor.fetchone()[0] == 1


def _fetch_existing_column_names_from_db(cursor: Cursor, table_name: str) -> list[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [column[1] for column in cursor.fetchall()]


def _fetch_field_names_from_model(model_fields: dict[str, FieldInfo]) -> list[str]:
    return list(model_fields.keys())


def _rename_columns_in_existing_table(
    cursor: Cursor, table_name: str, old_columns: list[str], new_columns: list[str]
) -> None:
    for old_column_name, new_column_name in dict(zip(old_columns, new_columns)).items():
        cursor.execute(
            f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name}"
        )


def _add_new_columns_to_existing_table(
    cursor: Cursor,
    table_name: str,
    model_fields: dict[str, FieldInfo],
    existing_columns: list[str],
) -> None:
    for field_name, field_info in model_fields.items():
        if field_name in existing_columns:
            continue
        column_definition = _prepare_column_definition(field_name, field_info)
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")


def _drop_columns_from_existing_table(
    cursor: Cursor, table_name: str, existing_columns: list[str], new_columns: list[str]
) -> None:
    columns_to_drop = set(existing_columns) - set(new_columns)
    for column_name in columns_to_drop:
        cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
