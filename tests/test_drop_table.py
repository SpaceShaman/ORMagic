from ormagic.models import DBModel


def test_drop_table(cursor):
    cursor.execute("CREATE TABLE user (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    cursor.connection.commit()
    cursor.execute("INSERT INTO user (name, age) VALUES ('Alice', 25)")
    cursor.connection.commit()

    class User(DBModel):
        name: str
        age: int

    User.drop_table()

    res = cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == []
