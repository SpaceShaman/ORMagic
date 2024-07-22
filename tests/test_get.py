from datetime import datetime
from sqlite3 import OperationalError

import pytest

from ormagic.models import DBModel, ObjectNotFound


@pytest.fixture
def prepare_db(db_cursor):
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    )
    db_cursor.connection.commit()
    data = [("John", 30), ("Jane", 25), ("Doe", 35), ("John", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()


class User(DBModel):
    name: str
    age: int


def test_get_object_from_db(prepare_db):
    user = User.get(id=2)

    assert user.id == 2
    assert user.name == "Jane"
    assert user.age == 25


def test_get_object_from_db_by_name(prepare_db):
    user = User.get(name="Doe")

    assert user.id == 3
    assert user.name == "Doe"
    assert user.age == 35


def test_get_object_from_db_with_multiple_conditions(prepare_db):
    user = User.get(name="John", age=30)

    assert user.id == 1
    assert user.name == "John"
    assert user.age == 30


def test_try_to_get_non_existing_object_from_db(prepare_db):
    with pytest.raises(ObjectNotFound):
        User.get(id=100)


def test_try_to_get_object_from_db_with_wrong_condition(prepare_db):
    with pytest.raises(OperationalError):
        User.get(wrong_field="John")


def test_get_object_from_db_with_datetime_field(prepare_db, db_cursor):
    class UserWithDatetime(DBModel):
        name: str
        created_at: datetime

    UserWithDatetime.create_table()
    UserWithDatetime(name="John", created_at=datetime(2022, 3, 1, 12, 0, 0)).save()

    user_from_db = UserWithDatetime.get(id=1)
    assert user_from_db.id == 1
    assert user_from_db.name == "John"
    assert user_from_db.created_at == datetime(2022, 3, 1, 12, 0, 0)
