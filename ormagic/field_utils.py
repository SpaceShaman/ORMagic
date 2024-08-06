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
