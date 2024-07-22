import pytest

from ormagic.models import DBModel, ObjectNotFound


@pytest.fixture
def prepare_db(db_cursor):
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    )
    db_cursor.connection.commit()


class User(DBModel):
    name: str
    age: int


def test_delete_object_from_db(prepare_db, db_cursor):
    db_cursor.execute("INSERT INTO user (name, age) VALUES ('John', 30)")
    db_cursor.connection.commit()

    User(id=1, name="Jane", age=25).delete()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == []


def test_try_delete_non_existing_object_in_db(prepare_db, db_cursor):
    with pytest.raises(ObjectNotFound):
        User(id=1, name="Jane", age=25).delete()
