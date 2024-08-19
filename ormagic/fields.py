from typing import Literal

from pydantic import Field

OnDelateType = Literal["CASCADE", "SET NULL", "SET DEFAULT", "RESTRICT", "NO ACTION"]


def DBField(
    *args,
    unique: bool = False,
    on_delete: OnDelateType = "CASCADE",
    primary_key: bool = False,
    **kwargs,
):
    """Custom field function that extends pydantic's Field with additional database-related arguments.

    Args:
        default (Any, optional): The default value of the field. Defaults to PydanticUndefined.
        unique (bool, optional): Whether the field should be unique. Defaults to False.
        on_delete (CASCADE | SET NULL | SET DEFAULT | RESTRICT | NO ACTION, optional): The action to take when the referenced object is deleted. Defaults to "CASCADE".
        other arguments: Any other arguments that pydantic's Field accepts.
    """
    json_schema_extra = {
        "unique": unique,
        "on_delete": on_delete,
        "primary_key": primary_key,
    }
    if primary_key and "default" not in kwargs:
        kwargs["default"] = None
    return Field(*args, **kwargs, json_schema_extra=json_schema_extra)
