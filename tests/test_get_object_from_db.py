from pydantic_db.models import DBModel


def test_get_object_from_db(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()
    data = [("John", 30), ("Jane", 25), ("Doe", 35)]
    db_cursor.executemany("INSERT INTO user (name, age) VALUES (?, ?)", data)
    db_cursor.connection.commit()

    user = User.get(id=2)

    assert user.name == "Jane"
    assert user.age == 25
