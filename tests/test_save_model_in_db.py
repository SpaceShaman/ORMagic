import pytest

from pydantic_db.models import DBModel


@pytest.fixture
def prepare_db(db_cursor):
    create_table_sql = "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    db_cursor.execute(create_table_sql)
    db_cursor.connection.commit()


class User(DBModel):
    name: str
    age: int


def test_save_data_to_db(prepare_db, db_cursor):
    User(name="John", age=30).save()
    User(name="Jane", age=25).save()
    User(name="Doe", age=35).save()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == [(1, "John", 30), (2, "Jane", 25), (3, "Doe", 35)]


def test_save_object_to_db_and_return_it_self(prepare_db):
    user = User(name="John", age=30).save()

    assert user.id == 1
    assert user.name == "John"
    assert user.age == 30


def test_override_object_in_db(prepare_db, db_cursor):
    db_cursor.execute("INSERT INTO user (name, age) VALUES ('John', 30)")
    db_cursor.connection.commit()

    User(id=1, name="Jane", age=25).save()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == [(1, "Jane", 25)]
