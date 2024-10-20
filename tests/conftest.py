import os

import pytest

from ormagic.sql_utils import get_cursor


@pytest.fixture
def db_cursor():
    with get_cursor() as cursor:
        yield cursor


@pytest.fixture(autouse=True)
def remove_db():
    yield
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
