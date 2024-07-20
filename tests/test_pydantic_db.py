from typing import Optional

from pydantic_db.models import DBModel


def test_create_db_table(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()

    res = db_cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
        (2, "age", "INTEGER", 1, None, 0),
    ]


def test_create_db_table_with_optional_field(db_cursor):
    class User(DBModel):
        name: str
        age: int
        optional_field: str | None = None
        another_optional_field: Optional[int] = None

    User.create_table()

    res = db_cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
        (2, "age", "INTEGER", 1, None, 0),
        (3, "optional_field", "TEXT", 0, None, 0),
        (4, "another_optional_field", "INTEGER", 0, None, 0),
    ]


def test_save_data_to_db(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()

    user = User(name="John", age=30)
    user.save()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == [(1, "John", 30)]
