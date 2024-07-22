from types import NoneType
from typing import Union

from ormagic.sql_utils import convert_to_sql_type


def test_convert_to_sql_type_int():
    assert convert_to_sql_type(int) == "INTEGER"


def test_convert_to_sql_type_str():
    assert convert_to_sql_type(str) == "TEXT"


def test_convert_to_sql_type_optional_int():
    assert convert_to_sql_type(Union[int, NoneType]) == "INTEGER"


def test_convert_to_sql_type_optional_str():
    assert convert_to_sql_type(Union[str, NoneType]) == "TEXT"
