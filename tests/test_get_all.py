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


def test_get_all_objects_from_db(db_cursor, prepare_db):
    data = [("John", 30), ("Jane", 25), ("Doe", 35), ("John", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()
    users = User.all()

    assert len(users) == 4
    assert all(isinstance(user, User) for user in users)
    assert users[0].id == 1
    assert users[0].name == "John"
    assert users[0].age == 30
    assert users[1].id == 2
    assert users[1].name == "Jane"
    assert users[1].age == 25
    assert users[2].id == 3
    assert users[2].name == "Doe"
    assert users[2].age == 35
    assert users[3].id == 4
    assert users[3].name == "John"
    assert users[3].age == 40


def test_get_all_objects_from_db_with_empty_table(db_cursor, prepare_db):
    users = User.all()

    assert len(users) == 0
    assert users == []
