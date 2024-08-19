from types import NoneType
from typing import Any, Literal, Union, get_args

from pydantic.fields import FieldInfo


def is_many_to_many_field(field_annotation: Any) -> bool:
    from .models import DBModel

    return bool(
        hasattr(field_annotation, "__origin__")
        and getattr(field_annotation, "__origin__") is list
        and issubclass(getattr(field_annotation, "__args__")[0], DBModel)
    )


def is_unique_field(field_info: FieldInfo) -> bool:
    return bool(
        field_info.json_schema_extra and field_info.json_schema_extra.get("unique")
    )


def is_primary_key_field(field_info: FieldInfo) -> bool:
    return bool(
        field_info.json_schema_extra and field_info.json_schema_extra.get("primary_key")
    )


def transform_field_annotation_to_sql_type(
    annotation: Any,
) -> Literal["INTEGER", "TEXT"]:
    from .models import DBModel

    if annotation in [int, Union[int, NoneType]]:
        return "INTEGER"
    types_tuple = get_args(annotation)
    if not types_tuple and issubclass(annotation, DBModel):
        return "INTEGER"
    if types_tuple and issubclass(types_tuple[0], DBModel):
        return "INTEGER"
    return "TEXT"


def get_on_delete_action(
    field_info: FieldInfo,
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


def _extract_field_operator(field: str) -> tuple[str, str]:
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
        operator = "LIKE"
    elif operator == "nlike":
        operator = "NOT LIKE"
    elif operator == "in":
        operator = "IN"
    elif operator == "nin":
        operator = "NOT IN"
    elif operator == "between":
        operator = "BETWEEN"
    elif operator == "nbetween":
        operator = "NOT BETWEEN"
    else:
        raise ValueError(f"Invalid operator: {operator}")
    return field, operator


def prepare_where_conditions(*args, **kwargs) -> tuple[str, list]:
    from .query import Q

    conditions = []
    params = []
    for field, value in kwargs.items():
        if field in ("order_by", "limit", "offset"):
            continue
        field, operator = _extract_field_operator(field)
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
    for arg in args:
        if isinstance(arg, Q):
            conditions.append(arg.conditions)
            params.extend(arg.params)
    return " AND ".join(conditions), params
