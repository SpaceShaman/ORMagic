from types import NoneType
from typing import Union

from pydantic_db.sql_utils import get_sql_type


def test_get_sql_type_int():
    assert get_sql_type(int) == "INTEGER"


def test_get_sql_type_str():
    assert get_sql_type(str) == "TEXT"


def test_get_sql_type_optional_int():
    assert get_sql_type(Union[int, NoneType]) == "INTEGER"


def test_get_sql_type_optional_str():
    assert get_sql_type(Union[str, NoneType]) == "TEXT"
