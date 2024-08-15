import pytest

from ormagic import DBModel, Q


@pytest.fixture
def prepare_db(db_cursor):
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    )
    db_cursor.connection.commit()
    data = [("Alice", 30), ("Bob", 25), ("Charlie", 35), ("David", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()


def test_filter_two_fields_with_q_objects_or_operator(prepare_db):
    class User(DBModel):
        name: str
        age: int

    users = User.filter(Q(name="Alice") | Q(age=25))

    assert len(users) == 2
    assert all(isinstance(user, DBModel) for user in users)
    assert users[0].id == 1
    assert users[0].name == "Alice"
    assert users[0].age == 30
    assert users[1].id == 2
    assert users[1].name == "Bob"
    assert users[1].age == 25


def test_filter_with_two_q_objects(prepare_db):
    class User(DBModel):
        name: str
        age: int

    users = User.filter(Q(age__gt=25), Q(age__lte=35))

    assert len(users) == 2
    assert all(isinstance(user, DBModel) for user in users)
    assert users[0].id == 1
    assert users[0].name == "Alice"
    assert users[0].age == 30
    assert users[1].id == 3
    assert users[1].name == "Charlie"
    assert users[1].age == 35


def test_filter_with_q_object_and_keyword_arguments(prepare_db):
    class User(DBModel):
        name: str
        age: int

    users = User.filter(Q(age__gt=25), age__lt=35)

    assert len(users) == 1
    assert isinstance(users[0], DBModel)
    assert users[0].id == 1
    assert users[0].name == "Alice"
    assert users[0].age == 30


def test_create_q_object_with_equal_operator():
    q = Q(name="Alice")

    assert q.conditions == "name = ?"
    assert q.params == ["Alice"]


def test_create_q_object_with_not_equal_operator():
    q = ~Q(name="Alice")

    assert q.conditions == "NOT (name = ?)"
    assert q.params == ["Alice"]


def test_create_q_object_with_two_operators():
    q = Q(name="Alice", age__gt=25)

    assert q.conditions == "name = ? AND age > ?"
    assert q.params == ["Alice", 25]


def test_combine_two_q_objects_with_or_operator():
    q1 = Q(name="Alice")
    q2 = Q(age__lt=25)
    q = q1 | q2

    assert q.conditions == "name = ? OR age < ?"
    assert q.params == ["Alice", 25]


def test_combine_two_q_objects_with_and_operator():
    q1 = Q(age__between=(25, 35))
    q2 = Q(weight__gte=70)
    q = q1 & q2

    assert q.conditions == "age BETWEEN ? AND ? AND weight >= ?"
    assert q.params == [25, 35, 70]


def test_combine_two_q_objects_with_or_not_operator():
    q1 = Q(name="Alice")
    q2 = Q(age__lt=25)
    q = q1 | ~q2

    assert q.conditions == "name = ? OR NOT (age < ?)"
    assert q.params == ["Alice", 25]


def test_combine_three_q_objects_with_and_or_operators():
    q1 = Q(name="Alice")
    q2 = Q(age__lt=25)
    q3 = Q(weight__gte=70)
    q = q1 & q2 | q3

    assert q.conditions == "name = ? AND age < ? OR weight >= ?"
    assert q.params == ["Alice", 25, 70]
