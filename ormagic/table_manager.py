from typing import Any, Type, get_args

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .field_utils import (
    get_on_delete_action,
    is_many_to_many_field,
    is_unique_field,
    transform_field_annotation_to_sql_type,
)
from .sql_utils import execute_sql


def create_table(table_name: str, model_fields: dict[str, FieldInfo]):
    columns = ["id INTEGER PRIMARY KEY"]
    for field_name, field_info in model_fields.items():
        if field_name == "id":
            continue
        if is_many_to_many_field(field_info.annotation):
            _create_intermediate_table(table_name, field_info)
            continue
        columns.append(_prepare_column_definition(field_name, field_info))

    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
    cursor = execute_sql(sql)
    cursor.connection.close()


def update_table(table_name: str, model_fields: dict[str, FieldInfo]) -> None:
    if not _is_table_exists(table_name):
        return create_table(table_name, model_fields)
    existing_columns = _fetch_existing_column_names_from_db(table_name)
    new_columns = _fetch_field_names_from_model(model_fields)
    if existing_columns == new_columns:
        return
    elif len(existing_columns) == len(new_columns):
        return _rename_columns_in_existing_table(
            table_name, existing_columns, new_columns
        )
    _add_new_columns_to_existing_table(table_name, model_fields, existing_columns)


def drop_table(table_name: str) -> None:
    cursor = execute_sql(f"DROP TABLE IF EXISTS {table_name}")
    cursor.connection.close()


def get_foreign_key_model(field_annotation: Any) -> Type | None:
    from .models import DBModel

    types_tuple = get_args(field_annotation)
    if not types_tuple and field_annotation and issubclass(field_annotation, DBModel):
        return field_annotation
    if types_tuple and issubclass(types_tuple[0], DBModel):
        return types_tuple[0]


def _create_intermediate_table(table_name: str, field_info: FieldInfo) -> None:
    related_table_name = getattr(field_info.annotation, "__args__")[0].__name__.lower()
    if _get_intermediate_table_name(table_name, related_table_name):
        return
    execute_sql(
        f"CREATE TABLE IF NOT EXISTS {table_name}_{related_table_name} ("
        "id INTEGER PRIMARY KEY, "
        f"{table_name}_id INTEGER, "
        f"{related_table_name}_id INTEGER, "
        f"FOREIGN KEY ({table_name}_id) REFERENCES {table_name}(id) ON DELETE CASCADE, "
        f"FOREIGN KEY ({related_table_name}_id) REFERENCES {related_table_name}(id) ON DELETE CASCADE)"
    )


def _get_intermediate_table_name(
    table_name: str, related_table_name: str
) -> str | None:
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
        column_definition += f", FOREIGN KEY ({field_name}) REFERENCES {foreign_model.__name__.lower()}(id) ON UPDATE {action} ON DELETE {action}"
    return column_definition


def _is_table_exists(table_name: str) -> bool:
    cursor = execute_sql(
        f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    exist = cursor.fetchone()[0] == 1
    cursor.connection.close()
    return exist


def _fetch_existing_column_names_from_db(table_name: str) -> list[str]:
    cursor = execute_sql(f"PRAGMA table_info({table_name})")
    existed_fields = [column[1] for column in cursor.fetchall()]
    cursor.connection.close()
    return existed_fields


def _fetch_field_names_from_model(model_fields: dict[str, FieldInfo]) -> list[str]:
    return list(model_fields.keys())


def _rename_columns_in_existing_table(
    table_name: str, old_columns: list[str], new_columns: list[str]
) -> None:
    for old_column_name, new_column_name in dict(zip(old_columns, new_columns)).items():
        cursor = execute_sql(
            f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name}"
        )
        cursor.connection.close()


def _add_new_columns_to_existing_table(
    table_name: str,
    model_fields: dict[str, FieldInfo],
    existing_columns: list[str],
) -> None:
    for field_name, field_info in model_fields.items():
        if field_name in existing_columns:
            continue
        column_definition = _prepare_column_definition(field_name, field_info)
        cursor = execute_sql(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
        cursor.connection.close()
