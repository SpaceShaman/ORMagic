from pydantic_db.models import DBModel


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
