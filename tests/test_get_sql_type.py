from types import NoneType
from typing import Union

from pydantic_db.models import DBModel


def test_get_sql_type_int():
    assert DBModel._get_sql_type(int) == "INTEGER"


def test_get_sql_type_str():
    assert DBModel._get_sql_type(str) == "TEXT"


def test_get_sql_type_optional_int():
    assert DBModel._get_sql_type(Union[int, NoneType]) == "INTEGER"


def test_get_sql_type_optional_str():
    assert DBModel._get_sql_type(Union[str, NoneType]) == "TEXT"
