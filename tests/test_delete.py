from sqlite3 import IntegrityError

import pytest
from psycopg2.errors import ForeignKeyViolation

from ormagic import DBField, DBModel
from ormagic.settings import Settings


@pytest.fixture
def prepare_db(cursor):
    if Settings().db_type == "postgresql":
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
        )
    else:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
        )
    cursor.connection.commit()


class User(DBModel):
    name: str
    age: int


def test_delete_object_from_db(prepare_db, cursor):
    cursor.execute("INSERT INTO users (name, age) VALUES ('John', 30)")
    cursor.connection.commit()

    User(id=1, name="Jane", age=25).delete()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    assert data == []


def test_delete_object_with_foreign_key_cascade(prepare_db, cursor):
    class Post(DBModel):
        title: str
        author: User = DBField(on_delete="CASCADE")

    Post.create_table()
    user = User(name="John", age=30).save()
    Post(title="First post", author=user).save()

    user.delete()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    assert data == []

    cursor.execute("SELECT * FROM posts")
    data = cursor.fetchall()
    assert data == []


def test_delete_object_with_foreign_key_cascade_by_default(prepare_db, cursor):
    class Post(DBModel):
        title: str
        author: User

    Post.create_table()
    user = User(name="John", age=30).save()
    Post(title="First post", author=user).save()

    user.delete()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    assert data == []

    cursor.execute("SELECT * FROM posts")
    data = cursor.fetchall()
    assert data == []


def test_delete_object_with_foreign_key_set_null(prepare_db, cursor):
    class Post(DBModel):
        title: str
        author: User = DBField(default=None, on_delete="SET NULL")

    Post.create_table()
    user = User(name="John", age=30).save()
    Post(title="First post", author=user).save()

    user.delete()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    assert data == []

    cursor.execute("SELECT * FROM posts")
    data = cursor.fetchall()
    assert data == [(1, "First post", None)]


def test_delete_object_with_foreign_key_restrict(prepare_db, cursor):
    class Post(DBModel):
        title: str
        author: User = DBField(on_delete="RESTRICT")

    Post.create_table()
    user = User(name="John", age=30).save()
    Post(title="First post", author=user).save()

    with pytest.raises((IntegrityError, ForeignKeyViolation)):
        user.delete()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    assert data == [(1, "John", 30)]

    cursor.execute("SELECT * FROM posts")
    data = cursor.fetchall()
    assert data == [(1, "First post", 1)]


def test_delete_object_with_foreign_key_set_default(prepare_db, cursor):
    class Post(DBModel):
        title: str
        author: User = DBField(default=1, on_delete="SET DEFAULT")

    Post.create_table()
    User(name="Jane", age=25).save()
    user = User(name="John", age=30).save()
    Post(title="First post", author=user).save()

    user.delete()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    assert data == [(1, "Jane", 25)]

    cursor.execute("SELECT * FROM posts")
    data = cursor.fetchall()
    assert data == [(1, "First post", 1)]


def test_delete_object_with_foreign_key_no_action(prepare_db, cursor):
    class Post(DBModel):
        title: str
        author: User = DBField(on_delete="NO ACTION")

    Post.create_table()
    user = User(name="John", age=30).save()
    Post(title="First post", author=user).save()

    with pytest.raises((IntegrityError, ForeignKeyViolation)):
        user.delete()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    assert data == [(1, "John", 30)]

    cursor.execute("SELECT * FROM posts")
    data = cursor.fetchall()
    assert data == [(1, "First post", 1)]
