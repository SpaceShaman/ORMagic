import pytest

from pydantic_db.models import DBModel, NotExist


def test_get_object_from_db(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()
    data = [("John", 30), ("Jane", 25), ("Doe", 35)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()

    user = User.get(id=2)

    assert user.name == "Jane"
    assert user.age == 25


def test_get_object_from_db_by_name(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()
    data = [("John", 30), ("Jane", 25), ("Doe", 35)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()

    user = User.get(name="Doe")

    assert user.name == "Doe"
    assert user.age == 35


def test_try_to_get_non_existing_object_from_db(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()

    with pytest.raises(NotExist):
        User.get(id=1)
