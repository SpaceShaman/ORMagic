from sqlite3 import OperationalError

import pytest

from ormagic.models import DBModel


@pytest.fixture
def prepare_db(db_cursor):
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    )
    db_cursor.connection.commit()


class User(DBModel):
    name: str
    age: int


def test_filter_objects_with_the_same_value(prepare_db, db_cursor):
    data = [("John", 30), ("Jane", 25), ("Doe", 35), ("John", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()
    users = User.filter(name="John")

    assert len(users) == 2
    assert all(isinstance(user, User) for user in users)
    assert users[0].id == 1
    assert users[0].name == "John"
    assert users[0].age == 30
    assert users[1].id == 4
    assert users[1].name == "John"
    assert users[1].age == 40


def test_filter_objects_with_multiple_values(prepare_db, db_cursor):
    data = [("John", 30), ("Jane", 25), ("Doe", 35), ("John", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()
    users = User.filter(name="John", age=40)

    assert len(users) == 1
    assert isinstance(users[0], User)
    assert users[0].id == 4
    assert users[0].name == "John"
    assert users[0].age == 40


def test_filter_objects_with_no_results(prepare_db, db_cursor):
    data = [("John", 30), ("Jane", 25), ("Doe", 35), ("John", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()
    users = User.filter(name="Jane", age=30)

    assert len(users) == 0


def test_try_to_filter_objects_with_invalid_field(prepare_db, db_cursor):
    data = [("John", 30), ("Jane", 25), ("Doe", 35), ("John", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()

    with pytest.raises(OperationalError):
        User.filter(invalid_field="Jane")
