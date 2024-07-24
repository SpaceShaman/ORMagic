from sqlite3 import IntegrityError

import pytest
from pydantic import Field

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


def test_delete_object_with_foreign_key_cascade(prepare_db, db_cursor):
    db_cursor.execute("PRAGMA foreign_keys")
    result = db_cursor.fetchone()
    assert result[0] == 1

    class Post(DBModel):
        title: str
        user: User = Field(on_delete="CASCADE")  # type: ignore

    Post.create_table()
    user = User(name="John", age=30).save()
    Post(title="First post", user=user).save()

    user.delete()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == []

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == []


def test_delete_object_with_foreign_key_cascade_by_default(prepare_db, db_cursor):
    class Post(DBModel):
        title: str
        user: User

    Post.create_table()
    user = User(name="John", age=30).save()
    Post(title="First post", user=user).save()

    user.delete()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == []

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == []


def test_delete_object_with_foreign_key_set_null(prepare_db, db_cursor):
    class Post(DBModel):
        title: str
        user: User = Field(default=None, on_delete="SET_NULL")  # type: ignore

    Post.create_table()
    user = User(name="John", age=30).save()
    Post(title="First post", user=user).save()

    user.delete()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == []

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == [(1, "First post", None)]


def test_delete_object_with_foreign_key_restrict(prepare_db, db_cursor):
    class Post(DBModel):
        title: str
        user: User = Field(on_delete="RESTRICT")  # type: ignore

    Post.create_table()
    user = User(name="John", age=30).save()
    Post(title="First post", user=user).save()

    with pytest.raises(IntegrityError):
        user.delete()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == [(1, "John", 30)]

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == [(1, "First post", 1)]


def test_delete_object_with_foreign_key_set_default(prepare_db, db_cursor):
    class Post(DBModel):
        title: str
        user: User = Field(default=1, on_delete="SET_DEFAULT")  # type: ignore

    Post.create_table()
    User(name="Jane", age=25).save()
    user = User(name="John", age=30).save()
    Post(title="First post", user=user).save()

    user.delete()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == [(1, "Jane", 25)]

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == [(1, "First post", 1)]
