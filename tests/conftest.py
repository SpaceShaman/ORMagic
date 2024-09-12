import os

import pytest

from ormagic.sql_utils import get_cursor


def remove_db():
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")


@pytest.fixture
def db_cursor():
    remove_db()
    with get_cursor() as cursor:
        yield cursor
    remove_db()
