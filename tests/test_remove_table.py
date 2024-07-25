from ormagic.models import DBModel


def test_remove_table(db_cursor):
    db_cursor.execute(
        "CREATE TABLE user (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
    )
    db_cursor.connection.commit()
    db_cursor.execute("INSERT INTO user (name, age) VALUES ('Alice', 25)")
    db_cursor.connection.commit()

    class User(DBModel):
        name: str
        age: int

    User.drop_table()

    res = db_cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == []
