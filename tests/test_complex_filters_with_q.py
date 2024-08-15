import pytest

from ormagic import Q


@pytest.fixture
def prepare_db(db_cursor):
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    )
    db_cursor.connection.commit()
    data = [("Alice", 30), ("Bob", 25), ("Charlie", 35), ("David", 40)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()


# def test_filter_two_fields_with_q_and_or_operator():
#     users = DBModel.filter(Q(name="Alice") | Q(age=25))

#     assert len(users) == 2
#     assert all(isinstance(user, DBModel) for user in users)
#     assert users[0].id == 1
#     assert users[0].name == "Alice"
#     assert users[0].age == 30
#     assert users[1].id == 2
#     assert users[1].name == "Bob"
#     assert users[1].age == 25


def test_create_q_object_with_equal_operator():
    q = Q(name="Alice")

    assert isinstance(q, Q)
    assert q.condition == "name = 'Alice'"
