from ormagic.models import DBModel

from .asserts import assert_table_schema


def test_drop_table(cursor):
    cursor.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
    )
    cursor.execute("INSERT INTO users (id, name, age) VALUES (0, 'Alice', 25)")
    cursor.connection.commit()

    class User(DBModel):
        name: str
        age: int

    User.drop_table()

    assert_table_schema(cursor, "users", [])
