from pydantic_db.models import DBModel


def test_save_data_to_db(db_cursor):
    class User(DBModel):
        name: str
        age: int

    User.create_table()

    User(name="John", age=30).save()
    User(name="Jane", age=25).save()
    User(name="Doe", age=35).save()

    res = db_cursor.execute("SELECT * FROM user")
    data = res.fetchall()
    assert data == [(1, "John", 30), (2, "Jane", 25), (3, "Doe", 35)]
