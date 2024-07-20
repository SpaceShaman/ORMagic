from pydantic_db.models import DBModel


def test_create_db_table(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()

    res = db_cursor.execute("PRAGMA table_info(user)")
    data = res.fetchall()
    assert data == [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 1, None, 0),
        (2, "age", "INTEGER", 1, None, 0),
    ]


def test_save_data_to_db(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()

    user = User(name="John", age=30)
    user.save()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == [(1, "John", 30)]
