from typing import Type, get_args

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .field_utils import (
    is_many_to_many_field,
    is_unique_field,
    transform_field_annotation_to_sql_type,
)
from .sql_utils import execute_sql


def create_table(cls, table_name: str, model_fields: dict[str, FieldInfo]):
    columns = ["id INTEGER PRIMARY KEY"]
    for field_name, field_info in model_fields.items():
        if field_name == "id":
            continue
        if is_many_to_many_field(field_info.annotation):
            _create_intermediate_table(table_name, field_info)
            continue
        columns.append(_prepare_column_definition(cls, field_name, field_info))

    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
    cursor = execute_sql(sql)
    cursor.connection.close()


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


def _prepare_column_definition(cls, field_name: str, field_info: FieldInfo) -> str:
    field_type = transform_field_annotation_to_sql_type(field_info.annotation)
    column_definition = f"{field_name} {field_type}"
    if field_info.default not in (PydanticUndefined, None):
        column_definition += f" DEFAULT '{field_info.default}'"
    if field_info.is_required():
        column_definition += " NOT NULL"
    if is_unique_field(field_info):
        column_definition += " UNIQUE"
    if foreign_model := get_foreign_key_model(cls, field_name):
        action = cls._get_on_delete_action(field_info)
        column_definition += f", FOREIGN KEY ({field_name}) REFERENCES {foreign_model.__name__.lower()}(id) ON UPDATE {action} ON DELETE {action}"
    return column_definition


def get_foreign_key_model(cls, field_name: str) -> Type | None:
    from .models import DBModel

    annotation = cls.model_fields[field_name].annotation
    types_tuple = get_args(annotation)
    if not types_tuple and annotation and issubclass(annotation, DBModel):
        return annotation
    if types_tuple and issubclass(types_tuple[0], DBModel):
        return types_tuple[0]
