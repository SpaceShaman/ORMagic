from typing import Optional

from ormagic.models import DBModel


def test_add_column_to_existing_table(db_cursor):
    db_cursor.execute(
        "CREATE TABLE user (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER NOT NULL)"
    )
    db_cursor.connection.commit()
    db_cursor.execute("INSERT INTO user (name, age) VALUES ('Alice', 25)")
    db_cursor.connection.commit()

    class User(DBModel):
        name: str
        age: int
        weight: Optional[int] = None

    User.update_table()

    res = db_cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
        (2, "age", "INTEGER", 1, None, 0),
        (3, "weight", "INTEGER", 0, None, 0),
    ]
