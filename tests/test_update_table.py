from sqlite3 import OperationalError
from typing import Optional

import pytest

from ormagic.fields import DBField
from ormagic.models import DBModel


@pytest.fixture(autouse=True)
def prepare_db(db_cursor):
    db_cursor.execute(
        "CREATE TABLE user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    )
    db_cursor.connection.commit()
    db_cursor.execute("INSERT INTO user (name, age) VALUES ('Alice', 25)")
    db_cursor.connection.commit()


def test_add_optional_column_to_existing_table(db_cursor):
    class User(DBModel):
        name: str
        age: int
        weight: Optional[int] = None

    User.update_table()

    res = db_cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
        (2, "age", "INTEGER", 1, None, 0),
        (3, "weight", "INTEGER", 0, None, 0),
    ]


def test_try_add_column_to_existing_table_with_not_null_constraint(db_cursor):
    class User(DBModel):
        name: str
        age: int
        weight: int

    with pytest.raises(OperationalError):
        User.update_table()


def test_try_add_column_to_existing_table_with_unique_constraint(db_cursor):
    class User(DBModel):
        name: str
        age: int
        weight: int = DBField(default=0, unique=True)

    with pytest.raises(OperationalError):
        User.update_table()


def test_add_column_to_existing_table_with_default_value(db_cursor):
    class User(DBModel):
        name: str
        age: int
        weight: int = 10

    User.update_table()

    res = db_cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
        (2, "age", "INTEGER", 1, None, 0),
        (3, "weight", "INTEGER", 0, "'10'", 0),
    ]
