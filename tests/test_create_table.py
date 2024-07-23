from typing import Optional

from ormagic.models import DBModel


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


def test_create_db_table_with_default_value(db_cursor):
    class User(DBModel):
        default_field: str = "default value"

    User.create_table()

    res = db_cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "default_field", "TEXT", 0, "'default value'", 0),
    ]


def test_create_db_tables_with_one_to_many_relationship(db_cursor):
    class User(DBModel):
        name: str

    class Post(DBModel):
        title: str
        user: User

    User.create_table()
    Post.create_table()

    res = db_cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
    ]

    res = db_cursor.execute("PRAGMA table_info(post)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "title", "TEXT", 1, None, 0),
        (2, "user", "INTEGER", 1, None, 0),
    ]
