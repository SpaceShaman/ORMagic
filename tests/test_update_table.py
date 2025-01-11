from typing import Optional

import pytest

from ormagic.fields import DBField
from ormagic.models import DBModel
from ormagic.settings import Settings

from .asserts import Column, assert_table_schema


@pytest.fixture(autouse=True)
def prepare_db(cursor):
    data = ("Alice", 25)
    if Settings().db_type == "postgresql":
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
        )
        cursor.connection.commit()
        cursor.execute("INSERT INTO users (name, age) VALUES (%s, %s)", data)
    else:
        cursor.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
        )
        cursor.connection.commit()
        cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", data)
    cursor.connection.commit()


def test_add_optional_column_to_existing_table(cursor):
    class User(DBModel):
        name: str
        age: int
        weight: Optional[int] = None

    User.update_table()

    assert_table_schema(
        cursor,
        "users",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="name", type="TEXT"),
            Column(name="age", type="INTEGER"),
            Column(name="weight", type="INTEGER"),
        ],
    )


def test_try_add_column_to_existing_table_with_not_null_constraint(cursor):
    class User(DBModel):
        name: str
        age: int
        weight: int

    with pytest.raises(Exception):
        User.update_table()


def test_try_add_column_to_existing_table_with_unique_constraint(cursor):
    class User(DBModel):
        name: str
        age: int
        weight: int = DBField(default=0, unique=True)

    with pytest.raises(Exception):
        User.update_table()


def test_add_column_to_existing_table_with_default_value(cursor):
    class User(DBModel):
        name: str
        age: int
        weight: int = 10

    User.update_table()

    assert_table_schema(
        cursor,
        "users",
        [
            Column(name="id", type="INTEGER", is_primary_key=True),
            Column(name="name", type="TEXT"),
            Column(name="age", type="INTEGER"),
            Column(name="weight", type="INTEGER", default="'10'"),
        ],
    )


def test_add_multiple_columns_to_existing_table(cursor):
    class User(DBModel):
        name: str
        age: int
        weight: int = 10
        height: int = 170

    User.update_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
        (2, "age", "INTEGER", 1, None, 0),
        (3, "weight", "INTEGER", 0, "'10'", 0),
        (4, "height", "INTEGER", 0, "'170'", 0),
    ]


def test_update_non_existing_table_will_create_a_new_one(cursor):
    class NonExistingTable(DBModel):
        name: str

    NonExistingTable.update_table()

    res = cursor.execute("PRAGMA table_info(nonexistingtable)")
    data = res.fetchall()
    assert data == [(0, "id", "INTEGER", 0, None, 1), (1, "name", "TEXT", 1, None, 0)]


def test_rename_column_in_existing_table(cursor):
    class User(DBModel):
        first_name: str
        age: int

    User.update_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "first_name", "TEXT", 1, None, 0),
        (2, "age", "INTEGER", 1, None, 0),
    ]


def test_rename_multiple_columns_in_existing_table(cursor):
    class User(DBModel):
        first_name: str
        years: int

    User.update_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "first_name", "TEXT", 1, None, 0),
        (2, "years", "INTEGER", 1, None, 0),
    ]


def test_try_update_table_without_changes(cursor):
    class User(DBModel):
        name: str
        age: int

    User.update_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
        (2, "age", "INTEGER", 1, None, 0),
    ]


def test_drop_column_from_existing_table(cursor):
    class User(DBModel):
        name: str

    User.update_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert len(data) == 2
    assert data == [(0, "id", "INTEGER", 0, None, 1), (1, "name", "TEXT", 1, None, 0)]


def test_drop_multiple_columns_from_existing_table(cursor):
    class User(DBModel):
        pass

    User.update_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert len(data) == 1
    assert data == [(0, "id", "INTEGER", 0, None, 1)]
