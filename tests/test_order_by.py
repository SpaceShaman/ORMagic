from sqlite3 import OperationalError

import pytest

from ormagic.models import DBModel


@pytest.fixture
def prepare_db(db_cursor):
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL, height INTEGER NOT NULL)"
    )
    db_cursor.connection.commit()
    data = [("John", 30, 180), ("Jane", 25, 190), ("Doe", 35, 170), ("John", 35, 160)]
    db_cursor.executemany("INSERT INTO user (name, age, height) VALUES (?, ?, ?)", data)
    db_cursor.connection.commit()


class User(DBModel):
    name: str
    age: int
    height: int


def test_order_by_asc(prepare_db, db_cursor):
    users = User.filter(order_by="age")

    assert len(users) == 4
    assert users[0].id == 2
    assert users[0].age == 25
    assert users[1].id == 1
    assert users[1].age == 30
    assert users[2].id == 3
    assert users[2].age == 35
    assert users[3].id == 4
    assert users[3].age == 35


def test_order_by_desc(prepare_db, db_cursor):
    users = User.filter(order_by="-age")

    assert len(users) == 4
    assert users[0].id == 3
    assert users[0].age == 35
    assert users[1].id == 4
    assert users[1].age == 35
    assert users[2].id == 1
    assert users[2].age == 30
    assert users[3].id == 2
    assert users[3].age == 25


def test_order_by_multiple_asc(prepare_db, db_cursor):
    users = User.filter(order_by=("age", "height"))

    assert len(users) == 4
    assert users[0].id == 2
    assert users[0].age == 25
    assert users[0].height == 190
    assert users[1].id == 1
    assert users[1].age == 30
    assert users[1].height == 180
    assert users[2].id == 4
    assert users[2].age == 35
    assert users[2].height == 160
    assert users[3].id == 3
    assert users[3].age == 35
    assert users[3].height == 170


def test_order_by_multiple_desc(prepare_db, db_cursor):
    users = User.filter(order_by=("-age", "-height"))

    assert len(users) == 4
    assert users[0].id == 3
    assert users[0].age == 35
    assert users[0].height == 170
    assert users[1].id == 4
    assert users[1].age == 35
    assert users[1].height == 160
    assert users[2].id == 1
    assert users[2].age == 30
    assert users[2].height == 180
    assert users[3].id == 2
    assert users[3].age == 25
    assert users[3].height == 190


def test_order_by_multiple_mixed(prepare_db, db_cursor):
    users = User.filter(order_by=("-age", "height"))

    assert len(users) == 4
    assert users[1].id == 3
    assert users[1].age == 35
    assert users[1].height == 170
    assert users[0].id == 4
    assert users[0].age == 35
    assert users[0].height == 160
    assert users[2].id == 1
    assert users[2].age == 30
    assert users[2].height == 180
    assert users[3].id == 2
    assert users[3].age == 25
    assert users[3].height == 190


def test_order_by_invalid_field(prepare_db, db_cursor):
    with pytest.raises(OperationalError):
        User.filter(order_by="invalid_field")
