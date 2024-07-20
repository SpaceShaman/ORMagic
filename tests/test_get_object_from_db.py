import pytest

from pydantic_db.models import DBModel, NotExist


@pytest.fixture
def prepare_db(db_cursor):
    create_table_sql = "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    db_cursor.execute(create_table_sql)
    db_cursor.connection.commit()
    data = [("John", 30), ("Jane", 25), ("Doe", 35)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()


class User(DBModel):
    name: str
    age: int


def test_get_object_from_db(prepare_db):
    user = User.get(id=2)

    assert user.name == "Jane"
    assert user.age == 25


def test_get_object_from_db_by_name(prepare_db):
    user = User.get(name="Doe")

    assert user.name == "Doe"
    assert user.age == 35


def test_try_to_get_non_existing_object_from_db(prepare_db):
    with pytest.raises(NotExist):
        User.get(id=100)
