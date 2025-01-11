from datetime import datetime
from typing import Optional

import pytest

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


def assert_table_data(cursor, table_name, data):
    cursor.execute(f"SELECT * FROM {table_name}")
    table_data = cursor.fetchall()
    assert table_data == data


class User(DBModel):
    name: str
    age: int


def test_save_data_to_db(prepare_db, cursor):
    User(name="John", age=30).save()
    User(name="Jane", age=25).save()
    User(name="Doe", age=35).save()

    assert_table_data(
        cursor, "users", [(1, "John", 30), (2, "Jane", 25), (3, "Doe", 35)]
    )


def test_save_object_to_db_and_return_it_self(prepare_db):
    user = User(name="John", age=30).save()

    assert user.id == 1
    assert user.name == "John"
    assert user.age == 30


def test_override_object_in_db(prepare_db, cursor):
    cursor.execute("INSERT INTO users (name, age) VALUES ('John', 30)")
    cursor.connection.commit()

    User(id=1, name="Jane", age=25).save()

    assert_table_data(cursor, "users", [(1, "Jane", 25)])


def test_save_object_with_datetime_field_to_db(prepare_db, cursor):
    class UserWithDatetime(DBModel):
        name: str
        created_at: datetime

    UserWithDatetime.create_table()

    user = UserWithDatetime(
        name="John", created_at=datetime(2021, 1, 1, 12, 0, 0)
    ).save()

    assert_table_data(cursor, "userwithdatetimes", [(1, "John", "2021-01-01 12:00:00")])
    assert user.created_at == datetime(2021, 1, 1, 12, 0, 0)


def test_save_object_with_default_value_to_db(prepare_db, cursor):
    class UserWithDefault(DBModel):
        name: str
        age: int = 30

    UserWithDefault.create_table()

    user = UserWithDefault(name="John").save()

    assert_table_data(cursor, "userwithdefaults", [(1, "John", 30)])
    assert user.age == 30


def test_save_object_with_foreign_key_to_db(cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        author: User

    User.create_table()
    Post.create_table()

    user = User(name="John", age=30).save()
    post = Post(title="First post", author=user).save()

    assert_table_data(cursor, "posts", [(1, "First post", 1)])
    assert post.author.id == user.id


def test_override_object_with_foreign_key_in_db(cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        author: User

    User.create_table()
    Post.create_table()

    user = User(name="John", age=30).save()
    post = Post(title="First post", author=user).save()

    new_user = User(name="Jane", age=25).save()
    post.author = new_user
    post.save()

    assert_table_data(cursor, "posts", [(1, "First post", 2)])
    assert post.author.id == new_user.id


def test_save_object_with_foreign_key_for_non_existing_foreign_object(cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        author: User

    User.create_table()
    Post.create_table()

    post = Post(title="First post", author=User(name="John", age=30)).save()

    assert_table_data(cursor, "posts", [(1, "First post", 1)])
    assert_table_data(cursor, "users", [(1, "John", 30)])
    assert post.title == "First post"
    assert post.author.id == 1
    assert post.author.name == "John"
    assert post.author.age == 30


def test_save_object_with_optional_foreign_key_not_set(cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        author: User | None = None

    User.create_table()
    Post.create_table()

    post = Post(title="First post").save()

    assert_table_data(cursor, "posts", [(1, "First post", None)])
    assert post.title == "First post"
    assert post.author is None


def test_overide_object_with_optional_foreign_key_not_set(cursor):
    class User(DBModel):
        name: str

    class Post(DBModel):
        title: str
        author: User | None = None

    User.create_table()
    Post.create_table()

    user = User(name="John").save()
    post = Post(title="First post", author=user).save()
    post.author = None
    post.save()

    assert_table_data(cursor, "posts", [(1, "First post", None)])


def test_save_object_with_optional_foreign_key_set(cursor):
    class User(DBModel):
        name: str
        age: int

    class Post(DBModel):
        title: str
        author: Optional[User] = None

    User.create_table()
    Post.create_table()

    user = User(name="John", age=30).save()
    post = Post(title="First post", author=user).save()

    assert_table_data(cursor, "posts", [(1, "First post", 1)])
    assert post.title == "First post"
    assert post.author.id == 1  # type: ignore
    assert post.author.name == "John"  # type: ignore
    assert post.author.age == 30  # type: ignore


def test_try_save_two_objects_with_same_values_for_unique_field(cursor):
    class User(DBModel):
        name: str = DBField(unique=True)
        age: int

    User.create_table()

    User(name="John", age=30).save()

    with pytest.raises(Exception):
        User(name="John", age=20).save()


def test_save_object_with_many_to_many_relationship(cursor):
    class User(DBModel):
        name: str
        courses: list["Course"] = []

    class Course(DBModel):
        name: str
        users: list[User] = []

    User.create_table()
    Course.create_table()

    course_0 = Course(name="Python").save()
    course_1 = Course(name="JavaScript").save()
    course_2 = Course(name="Java").save()
    User(name="John", courses=[course_0, course_1]).save()
    User(name="Jane", courses=[course_1, course_2]).save()

    assert_table_data(cursor, "users", [(1, "John"), (2, "Jane")])

    assert_table_data(
        cursor, "courses", [(1, "Python"), (2, "JavaScript"), (3, "Java")]
    )
    assert_table_data(
        cursor, "courses_users", [(1, 1, 1), (2, 2, 1), (3, 2, 2), (4, 3, 2)]
    )


def test_save_object_with_many_to_many_relationship_for_non_existing_objects(cursor):
    class User(DBModel):
        name: str
        courses: list["Course"] = []

    class Course(DBModel):
        name: str
        users: list[User] = []

    User.create_table()
    Course.create_table()

    course_0 = Course(name="Python")
    course_1 = Course(name="JavaScript")
    Course(name="Java")
    User(name="John", courses=[course_0, course_1]).save()

    assert_table_data(cursor, "users", [(1, "John")])
    assert_table_data(cursor, "courses", [(1, "Python"), (2, "JavaScript")])
    assert_table_data(cursor, "courses_users", [(1, 1, 1), (2, 2, 1)])


def test_save_object_with_many_to_many_relationship_without_related_objects(cursor):
    class User(DBModel):
        name: str
        courses: list["Course"] = []

    class Course(DBModel):
        name: str
        users: list[User] = []

    User.create_table()
    Course.create_table()

    User(name="John").save()

    assert_table_data(cursor, "users", [(1, "John")])
    assert_table_data(cursor, "courses", [])
    assert_table_data(cursor, "courses_users", [])


def test_override_object_with_many_to_many_relationship(cursor):
    class User(DBModel):
        name: str
        courses: list["Course"] = []

    class Course(DBModel):
        name: str
        users: list[User] = []

    User.create_table()
    Course.create_table()

    course_0 = Course(name="Python").save()
    course_1 = Course(name="JavaScript").save()
    course_2 = Course(name="Java").save()
    user = User(name="John", courses=[course_0, course_1]).save()
    user.courses = [course_2]
    user.save()

    assert_table_data(cursor, "users", [(1, "John")])
    assert_table_data(
        cursor, "courses", [(1, "Python"), (2, "JavaScript"), (3, "Java")]
    )
    # sourcery skip: no-conditionals-in-tests
    if Settings().db_type == "postgresql":
        assert_table_data(cursor, "courses_users", [(3, 3, 1)])
    else:
        assert_table_data(cursor, "courses_users", [(1, 3, 1)])


def test_save_object_with_custom_primary_key_field_autoincrement(cursor):
    class User(DBModel):
        custom_id: int = DBField(primary_key=True)
        name: str

    User.create_table()

    User(name="John").save()

    assert_table_data(cursor, "users", [(1, "John")])


def test_save_object_with_custom_primary_key_field_and_set_id(cursor):
    class User(DBModel):
        custom_id: int = DBField(primary_key=True)
        name: str

    User.create_table()

    User(custom_id=10, name="John").save()

    assert_table_data(cursor, "users", [(10, "John")])


def test_override_object_with_custom_primary_key_field(cursor):
    class User(DBModel):
        custom_id: int = DBField(primary_key=True)
        name: str

    User.create_table()

    User(custom_id=10, name="John").save()
    User(custom_id=10, name="Jane").save()

    assert_table_data(cursor, "users", [(10, "Jane")])
