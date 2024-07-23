from datetime import datetime
from typing import Optional

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


def test_try_override_non_existing_object_in_db(prepare_db, db_cursor):
    with pytest.raises(ObjectNotFound):
        User(id=1, name="Jane", age=25).save()


def test_save_object_with_datetime_field_to_db(prepare_db, db_cursor):
    class UserWithDatetime(DBModel):
        name: str
        created_at: datetime

    UserWithDatetime.create_table()

    user = UserWithDatetime(
        name="John", created_at=datetime(2021, 1, 1, 12, 0, 0)
    ).save()

    res = db_cursor.execute("SELECT * FROM userwithdatetime")
    data = res.fetchall()
    assert data == [(1, "John", "2021-01-01 12:00:00")]
    assert user.created_at == datetime(2021, 1, 1, 12, 0, 0)


def test_save_object_with_default_value_to_db(prepare_db, db_cursor):
    class UserWithDefault(DBModel):
        name: str
        age: int = 30

    UserWithDefault.create_table()

    user = UserWithDefault(name="John").save()

    res = db_cursor.execute("SELECT * FROM userwithdefault")
    data = res.fetchall()
    assert data == [(1, "John", 30)]
    assert user.age == 30


def test_save_object_with_foreign_key_to_db(db_cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        user: User

    User.create_table()
    Post.create_table()

    user = User(name="John", age=30).save()
    post = Post(title="First post", user=user).save()

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == [(1, "First post", 1)]
    assert post.user.id == user.id


def test_override_object_with_foreign_key_in_db(db_cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        user: User

    User.create_table()
    Post.create_table()

    user = User(name="John", age=30).save()
    post = Post(title="First post", user=user).save()

    new_user = User(name="Jane", age=25).save()
    post.user = new_user
    post.save()

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == [(1, "First post", 2)]
    assert post.user.id == new_user.id


def test_save_object_with_foreign_key_for_non_existing_foreign_object(db_cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        user: User

    User.create_table()
    Post.create_table()

    post = Post(title="First post", user=User(name="John", age=30)).save()

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == [(1, "First post", 1)]

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == [(1, "John", 30)]

    assert post.title == "First post"
    assert post.user.id == 1
    assert post.user.name == "John"
    assert post.user.age == 30


def test_save_object_with_optional_foreign_key_not_set(db_cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        user: User | None = None

    User.create_table()
    Post.create_table()

    post = Post(title="First post").save()

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == [(1, "First post", None)]

    assert post.title == "First post"
    assert post.user is None


def test_save_object_with_optional_foreign_key_set(db_cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        user: Optional[User] = None

    User.create_table()
    Post.create_table()

    user = User(name="John", age=30).save()
    post = Post(title="First post", user=user).save()

    res = db_cursor.execute("SELECT * FROM post")
    data = res.fetchall()
    assert data == [(1, "First post", 1)]

    assert post.title == "First post"
    assert post.user.id == 1  # type: ignore
    assert post.user.name == "John"  # type: ignore
    assert post.user.age == 30  # type: ignore
