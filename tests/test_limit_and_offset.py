import pytest

from ormagic.models import DBModel
from ormagic.settings import Settings


@pytest.fixture
def prepare_db(cursor):
    data = [
        ("Alice", 90),
        ("Bob", 80),
        ("Charlie", 70),
        ("David", 60),
        ("Eve", 50),
        ("Frank", 40),
        ("Grace", 30),
        ("Helen", 20),
        ("Ivy", 10),
    ]
    if Settings().db_type == "postgresql":
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
        )
        cursor.connection.commit()
        cursor.executemany("INSERT INTO users (name, age) VALUES (%s, %s)", data)
    else:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
        )
        cursor.connection.commit()
        cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", data)
    cursor.connection.commit()


class User(DBModel):
    name: str
    age: int


def test_get_all_with_limit(prepare_db):
    users = User.all(limit=5)

    assert len(users) == 5
    assert users[0].name == "Alice"
    assert users[-1].name == "Eve"


def test_get_all_with_limit_and_offset(prepare_db):
    users = User.all(limit=4, offset=3)

    assert len(users) == 4
    assert users[0].name == "David"
    assert users[-1].name == "Grace"


def test_get_all_with_limit_and_offset_and_order(prepare_db):
    users = User.all(limit=3, offset=2, order_by="age")

    assert len(users) == 3
    assert users[0].name == "Grace"
    assert users[1].name == "Frank"
    assert users[2].name == "Eve"


def test_filter_with_limit_and_offset(prepare_db):
    users = User.filter(age__between=(30, 70), limit=2, offset=1)

    assert len(users) == 2
    assert users[0].name == "David"
    assert users[1].name == "Eve"
