from typing import Any


def is_many_to_many_field(field_annotation: Any) -> bool:
    from .models import DBModel

    return bool(
        hasattr(field_annotation, "__origin__")
        and getattr(field_annotation, "__origin__") is list
        and issubclass(getattr(field_annotation, "__args__")[0], DBModel)
    )
